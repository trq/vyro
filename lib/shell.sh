configure() {
    :
}

pre_install() {
    :
}

install() {
    :
}
post_install() {
    :
}

main() {
    local action="$1"

    shift
    case "$action" in
        provision)
            source "$@"
            pre_install
            install
            post_install
            ;;
        configure)
            source "$@"
            configure
            ;;
    esac
}

main "$@"
