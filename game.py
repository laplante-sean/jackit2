'''
Sets up site deployment and starts game
'''

import os
import sys
import signal
import traceback
import argparse

from PyQt5.QtWidgets import QApplication

from jackit2.config import ConfigError
from jackit2 import run, MAIN_WINDOW
from deploy import SITE_DEPLOYMENT


def sigint_handler(_signum, _frame):
    '''
    Handle SIGINT (cntrl-c)
    '''
    print("Caught cntrl-c. Exiting...")
    MAIN_WINDOW.close()
    QApplication.quit()


def main():
    '''
    Entry Point. Exceptions are written to bugreport.txt
    '''
    argparse.ArgumentParser(description='JackIT 2.0! (New and improved)')
    signal.signal(signal.SIGINT, sigint_handler)  # Register our signal handler for cntrl-c

    try:
        run()  # Start the application
    except ConfigError as exc:
        print("Invalid config: {}. Please fix {}".format(str(exc), SITE_DEPLOYMENT.config_path))
        sys.exit(1)
    except BaseException as exc:
        path = os.path.join(SITE_DEPLOYMENT.base_path, "bugreport.txt")
        print("Exception during game execution!")
        print("See {} for details.".format(path))
        print("Exception: {}".format(str(exc)))

        # Write the bug file
        with open(path, 'w') as bugreport:
            traceback.print_exc(file=bugreport)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
