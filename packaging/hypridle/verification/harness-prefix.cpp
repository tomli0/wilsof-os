// Test seams only: real enterEventLoop body is appended by regression.py.
#include <atomic>
#include <array>
#include <chrono>
#include <condition_variable>
#include <cstdio>
#include <cstdlib>
#include <cerrno>
#include <exception>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>
#include <sys/poll.h>
#include <unistd.h>
using namespace std::chrono_literals;
static std::string scenario;
static std::thread::id mainThread;
static std::atomic<int> workerAlive{0}, calls{0}, dbus1{0}, dbus2{0}, reads{0}, dispatches{0}, flushes{0}, conditions{0}, spawns{0};
static std::atomic<bool> throwing{false};
struct WorkerLifetime {
    WorkerLifetime() { ++workerAlive; }
    ~WorkerLifetime() { --workerAlive; std::puts("WORKER_EXIT"); std::fflush(stdout); }
};
enum { CRIT, ERR, TRACE, LOG };
namespace Debug {
    template<class... Args> void log(int, const char*, Args&&...) {}
}
struct FakeBus {
    int id;
    struct Data { int fd; };
    Data getEventLoopPollData() { return {id}; }
    bool processPendingEvent() {
        if (scenario == "exception") {
            throwing = true;
            throw std::runtime_error("injected event-processing exception");
        }
        ++(id == 10 ? dbus1 : dbus2);
        return false;
    }
};
static int wl_display_get_fd(void*) { return 11; }
static int wl_display_flush(void*) { ++flushes; return 0; }
static int wl_display_prepare_read(void*) { return scenario == "wayland-dispatch" ? -1 : 0; }
static int wl_display_read_events(void*) { ++reads; return 0; }
static int wl_display_dispatch_pending(void*) {
    ++dispatches;
    if (scenario == "exception-poll") throw std::runtime_error("injected dispatch exception during poll");
    return 0;
}
static int wl_display_dispatch(void*) { ++dispatches; return 0; }
static int64_t nowMonotonic() { return 100; }
static bool runConditionCmd(const std::string&) { ++conditions; return scenario != "retry-false"; }
static void spawn(const std::string&) { ++spawns; }
static int injected_poll(pollfd* fds, nfds_t count, int timeout) {
    const int n = calls++;
    // Do not mutate shared revents while awaiting the consumer handshake.
    // (The unpatched upstream shares this array across the threads.)
    if (scenario == "exception-poll") return ::poll(nullptr, 0, timeout);
    if (scenario == "hard-error") { errno = EIO; return -1; }
    if (scenario == "hup" || scenario == "hup-dbus" || scenario == "hup-dbus2" || scenario == "pollerr" || scenario == "pollnval") {
        int index = scenario == "hup-dbus" ? 0 : scenario == "hup-dbus2" ? 2 : 1;
        fds[index].revents = scenario == "pollerr" ? POLLERR : scenario == "pollnval" ? POLLNVAL : POLLHUP;
        return 1;
    }
    if (scenario == "eintr" && n == 0) { errno = EINTR; return -1; }
    if (scenario == "retry" || scenario == "retry-false") {
        while (!conditions.load()) std::this_thread::sleep_for(1ms);
        fds[1].revents = POLLHUP;
        return 1;
    }
    const int eventCall = scenario == "eintr" ? 1 : 0;
    if (n == eventCall) {
        for (nfds_t i = 0; i < count; ++i) fds[i].revents = POLLIN;
        return static_cast<int>(count);
    }
    if (scenario == "exception") {
        while (!throwing.load()) std::this_thread::sleep_for(1ms);
        // Real bounded poll: exercise stop/join while a poll is outstanding.
        return ::poll(nullptr, 0, timeout);
    }
    while (!(dbus1.load() && (count == 2 || dbus2.load()) && dispatches.load())) std::this_thread::sleep_for(1ms);
    fds[1].revents = POLLHUP;
    return 1;
}
#define poll injected_poll
class CHypridle {
public:
    CHypridle() {
        m_sDBUSState.connection = std::make_unique<FakeBus>(10);
        if (scenario != "two-fds") m_sDBUSState.screenSaverServiceConnection = std::make_unique<FakeBus>(12);
        if (scenario == "retry" || scenario == "retry-false") m_sWaylandIdleState.listeners.push_back({true, 100, "condition", false, "timeout", 7});
    }
    ~CHypridle() {
        const bool main = std::this_thread::get_id() == mainThread;
        std::printf("CLEANUP main=%d worker_alive=%d calls=%d dbus1=%d dbus2=%d reads=%d dispatches=%d flushes=%d conditions=%d spawns=%d pending=%d retry_at=%ld\n",
            main, workerAlive.load(), calls.load(), dbus1.load(), dbus2.load(), reads.load(), dispatches.load(), flushes.load(), conditions.load(), spawns.load(),
            m_sWaylandIdleState.listeners.empty() ? 0 : m_sWaylandIdleState.listeners[0].conditionPending,
            m_sWaylandIdleState.listeners.empty() ? 0L : m_sWaylandIdleState.listeners[0].conditionRetryAt);
        std::fflush(stdout);
    }
    void run() { enterEventLoop(); }
    void enterEventLoop();
    // Exact termination declaration and event-loop internals are extracted below.
    TERMINATION_DECLARATION
    INTERNALS_DECLARATION
    struct { void* display = nullptr; } m_sWaylandState;
    struct { std::unique_ptr<FakeBus> connection, screenSaverServiceConnection; } m_sDBUSState;
    struct Listener { bool conditionPending; int64_t conditionRetryAt; std::string conditionCmd; bool onTimeoutFired; std::string onTimeout; int64_t conditionRetry; };
    struct { std::vector<Listener> listeners; } m_sWaylandIdleState;
};
inline std::unique_ptr<CHypridle> g_pHypridle;
