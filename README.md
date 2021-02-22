# bash-argparse-generator

Configure your bash' script options from a configuration file and ask python3 to gently generate the appropriate usage and parsing in the targeted shell file (or stdout).

You can ask for a "testing" part that will generate an additional zone where it prints the options.

## Usage

See help, it's better as is.

### Example of config details

When specifying the options, you can fill the following informations (using yaml as a reference):

* `options` : list of comma separated mix of short and/or long options.
* `destination` : variable to store the result.
* `has_argument` : one element of "no", "yes" and "self".
  * "no" means it will be treated as a boolean.
  * "yes" means it will take an argument.
  * "self" means that the option name is the wanted result itself (It is recommended to use only long-named options in this case).
* `help_text` : the help for this option.

## Valid configuration files

At the moment these three formats are managed:

* Yaml
* JSON
* CSV

Yaml and JSON files can manage the generator script custom options in additions to the bash options.
Doing this with the CSV part seems to bothersome to try.
