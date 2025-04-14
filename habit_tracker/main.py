import sys
from habit_tracker.cli import CLI
from habit_tracker.models import init_db

def main():
    init_db()
    cli = CLI()

    if len(sys.argv) > 1:
        cli.fire()
    else:
        cli.run()

if __name__ == '__main__':
    main()