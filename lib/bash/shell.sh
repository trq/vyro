#!/usr/bin/env bash
#
# This file is responsible for creating an environment that we
# can execute our package provisioning scripts within.
#
VYRO_ACTION="$1" ; shift
VYRO_LIB_DIR="$1" ; shift
VYRO_PROJECT_DIR="$1" ; shift

VYRO_BASE_PKG="$VYRO_LIB_DIR/bash/package.sh"
VYRO_PKG_LIBS="$VYRO_LIB_DIR/bash/libs.sh"
VYRO_ENV="$VYRO_LIB_DIR/bash/env.sh"

VYRO_PROJECT_ENV="$VYRO_PROJECT_DIR/.vyro/env.sh"
VYRO_PROJECT_HOOKS_DIR="$VYRO_PROJECT_DIR/.vyro/hooks"

# Create the enviroment by loading all relevant source files in the approriate order
VYRO_SOURCES=("$VYRO_ENV $VYRO_BASE_PKG $VYRO_PKG_LIBS $VYRO_PROJECT_ENV")
for src in ${VYRO_SOURCES[@]} ; do
    if [ -f "$src" ] ; then
        source "$src"
    fi
done

main() {
    case "$VYRO_ACTION" in
        provision)
            PKG_NAME="$1"
            PKG_PATH="$2"

            if [ -f "$PKG_PATH/package.sh" ] ; then
                source "$PKG_PATH/package.sh"

                # Inject our configuration variables.
                eval `vyro configure $PKG_NAME`

                # Execute the pre_provision hook
                if [ -f "$VYRO_PROJECT_HOOKS_DIR/pre_provision.sh" ] ; then
                    source "$VYRO_PROJECT_HOOKS_DIR/pre_provision.sh"
                fi

                pre_install
                install
                post_install

                # Execute the post_provision hook
                if [ -f "$VYRO_PROJECT_HOOKS_DIR/post_provision.sh" ] ; then
                    source "$VYRO_PROJECT_HOOKS_DIR/post_provision.sh"
                fi
            fi
            ;;
    esac
}

main "$@"
