class Prompter:

    def __init__(self, config):
        self.config = config

    def prompt(self):
        """
        Loop through all configuration options and prompt to configure.
        """
        try:
            for option, data in self.config.get('config').iteritems():
                if data.has_key('prompt') and data['prompt'].has_key('question') and data['prompt'].has_key('type'):
                    if data['prompt']['type'].lower() == 'bool':
                        value = self.handle_bool(option, data)

                    if data['prompt']['type'].lower() == 'choice':
                        if data['prompt'].has_key('choices'):
                            value = self.handle_choice(option, data)

                # Store the config option on the package config
                self.config.set(option, value)

            # Persist the package config
            self.config.persist()

        except KeyboardInterrupt:
            pass

    def __resolve_bool(self, value, default):
        return_val = default
        if value is not None:
            if isinstance(value, bool):
                return_val = value
            else:
                if value.lower() == 'y' or value.lower() == 'yes':
                    return_val = True
                elif value.lower() == 'n' or value.lower() == 'no':
                    return_val = False

        return return_val

    def handle_bool(self, option, data):
        if data.has_key('value') and data['value'] == True:
            p = ' (Y/n) '
        else:
            p = ' (y/N) '

        if data.has_key('value'):
            default = data['value']
        else:
            default = False

        answer = raw_input(data['prompt']['question'] + p)
        return self.__resolve_bool(answer, default)

    def handle_choice(self, option, data):
        choices = data['prompt']['choices']
        print data['prompt']['question']
        i = 1
        for choice in choices:
            if data.has_key('value') and data['value'] == choice:
                print "* [%d] %s" % (i, choice)
            else:
                print "  [%d] %s" % (i, choice)

            i += 1

        answer = raw_input('? ')
        if answer:
            answer = int(answer) - 1
        else:
            if data.has_key('value'):
                try:
                    answer = choices.index(data['value'])
                except ValueError:
                    pass

        if answer > -1 and answer < len(choices):
            return choices[answer]

        print "Not a valid option"
