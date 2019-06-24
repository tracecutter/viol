.. AUTO-GENERATED FILE - DO NOT EDIT!! Use `make ref`.
.. _reference:

Reference Guide
===============

viol
------------------------------------------------------------------------
.. code-block:: none

		Usage: viol [OPTIONS] COMMAND [ARGS]...
		
		  viol is a command line tool to administer the Viol Design.
		
		Options:
		  -V, --version         Show the version and exit.
		  -v, --verbose         Give more output. Increase verbosity: option is additive
		                        up to 3 times.
		  -q, --quiet           Give less output. Decrease verbosity: option is additive
		                        up to 3 times. (WARNING, ERROR, CRITICAL)
		  --log PATH            Path to a verbose appending log.
		  --color / --no-color  Enable/Suppress colored output.
		  --help                Show this message and exit.
		
		Commands:
		  completion  A helper command to be used for command completion.
		  help        Show help for commands.
		  scan        Viol scan command.

viol scan
------------------------------------------------------------------------
.. code-block:: none

		Usage: viol scan [OPTIONS]
		
		  Viol scan command.
		
		  Scan a viola image, deduce the geometry, and curve fit the instrument with a
		  combination of Bezier curves and Clothoids.
		
		Options:
		  -f, --filename PATH  Path to a scanned viol image.
		  --help               Show this message and exit.

viol completion
------------------------------------------------------------------------
.. code-block:: none

		Usage: viol completion [OPTIONS]
		
		  A helper command to be used for command completion.
		
		  Append the output of this command to your shell .rc file.  When executed,
		  striking tab during command line interaction will autocomplete and/or
		  suggest possible input.  Command options are enumerated if tab is struck
		  after the character '-' is input.
		
		Options:
		  --shell-type [bash|zsh]  A helper command to be used for command completion.
		  --help                   Show this message and exit.

viol help
------------------------------------------------------------------------
.. code-block:: none

		Usage: viol help [OPTIONS] [SUBCMD]
		
		  Show help for commands.
		
		  This command provides an alternative to --help option to provide usage
		  information.
		
		Options:
		  --help  Show this message and exit.

