// Controlled native ownership reproduction; no compositor or real disk needed.
#include "src/core/PortalManager.hpp"
#include "xdg-output-unstable-v1.hpp"
#include <csignal>
#include <iostream>
#include <sys/socket.h>
#include <unistd.h>

int main() {
    signal(SIGPIPE, SIG_IGN);
    int fds[2];
    if (socketpair(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0, fds)) return 2;
    g_pPortalManager = std::make_unique<CPortalManager>();
    auto* portal = g_pPortalManager.get();
    portal->m_sWaylandConnection.display = wl_display_connect_to_fd(fds[0]);
    if (!portal->m_sWaylandConnection.display) return 3;
    portal->m_sWaylandConnection.registry = makeShared<CCWlRegistry>(
        reinterpret_cast<wl_proxy*>(wl_display_get_registry(portal->m_sWaylandConnection.display)));
    portal->onGlobal(1, zxdg_output_manager_v1_interface.name, 3);
    portal->onGlobal(2, wl_output_interface.name, 4);
    if (portal->getAllOutputs().size() != 1 || !portal->getAllOutputs()[0]->xdgOutput) return 4;
    close(fds[1]);
    portal->releaseWayland();
    if (portal->m_sWaylandConnection.display || portal->m_sWaylandConnection.registry || !portal->getAllOutputs().empty()) return 5;
    portal->releaseWayland(); // idempotent release

    g_pPortalManager.reset();
    std::cout << "OWNERSHIP_TEARDOWN_PASS\n";
}
