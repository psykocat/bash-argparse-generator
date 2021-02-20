# bash-argparse-generator

Configure your bash' script options from a configuration file and ask python3 to gently generate the appropriate usage and parsing in the targeted shell file (or stdout).

You can ask for a "testing" part that will generate an additional zone where it prints the options.

## Usage

See help, it's better as is.

## Valid configuration files

At the moment these three formats are managed:

* Yaml
* JSON
* CSV

Yaml and JSON files can manage the generator script custom options in additions to the bash options.
Doing this with the CSV part seems to bothersome to try.
