def print_help_menu() -> None:

    print("=== OrbitOps Help Menu ===")
    print("position <CATNR>          Show current latitude, longitude, and altitude")
    print("teme <CATNR>              Show current TEME position and velocity")
    print("info <CATNR>              Show satellite catalog information")
    print("search <name>             Search for a satellite by name")
    print("distance <CATNR1> <CATNR2> Show distance between two satellites")
    print("watch <CATNR>             Continuously track a satellite's position")
    print("help                      Show this help menu")