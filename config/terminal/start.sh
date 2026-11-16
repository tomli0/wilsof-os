# Sourced by interactive shells only; never print in scripts or pipes.
case $- in
  *i*)
    if [ -t 1 ] && [ "${TERM:-dumb}" != dumb ] && command -v fastfetch >/dev/null 2>&1; then
      fastfetch --config "$HOME/.local/share/wilsof-os/fastfetch.json"
    fi
    ;;
esac
