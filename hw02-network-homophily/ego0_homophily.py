"""Run the gender-feature homophily analysis for ego 0."""

import sys

from homophily import main


if __name__ == "__main__":
    main(["--ego", "0", *sys.argv[1:]])
