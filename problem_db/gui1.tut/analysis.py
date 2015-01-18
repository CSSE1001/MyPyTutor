class CodeVisitor(TutorialNodeVisitor):
    pass  # we actually only need the default behaviour here :)


class Analyser(CodeAnalyser):
    def _analyse(self):
        # NB: this is actually quite a special analysis function, as we do
        # *everything* using static analysis (no testing)
        # this is an acceptable solution given that there is only one sensible
        # way to create the layout that we're after, and we're trying to teach
        # them the sensible way
        if not self.visitor.functions['pressed'].is_defined:
            self.add_error('You must not delete the pressed function')

        if not self.visitor.functions['create_layout'].is_defined:
            self.add_error('You need to define a create_layout function')
        elif len(self.visitor.functions['create_layout'].args) != 1:
            self.add_error('create_layout should accept exactly one argument')

        if len(self.visitor.functions['create_layout'].calls['Button']) != 2:
            self.add_error('You need to create two buttons')
        elif len(self.visitor.functions['create_layout'].calls['pack']) != 2:
            self.add_error('You need to pack both buttons')
        else:
            # created exactly two buttons, and called pack twice
            # (NB: no guarantee that they packed both buttons)
            function_def = self.visitor.functions['create_layout']
            frame_name = function_def.args[0]

            for n, btn in enumerate(function_def.calls['Button']):
                if not btn.args:
                    self.add_error(
                        'The first argument to the constructor for a tk '
                        'widget (such as Button) must be the name of its '
                        'master widget'
                    )
                elif btn.args[0] != frame_name:
                    self.add_error(
                        'You need to give {} as the first argument to '
                        'Button'.format(frame_name)
                    )

                if 'text' not in btn.keywords:
                    self.add_error(
                        'You need to give a label to your buttons'
                    )
                elif btn.keywords['text'] != 'Button{}'.format(n + 1):
                    self.add_error(
                        'Expected label of {}, but got {}'.format(
                            'Button{}'.format(n + 1), btn.keywords['text'],
                        )
                    )

            for pack in function_def.calls['pack']:
                if pack.args:
                    self.add_error(
                        'You should not give positional arguments to pack'
                    )

                if 'side' not in pack.keywords:
                    self.add_error(
                        'You need to provide side as a keyword argument to '
                        'pack (in {})'.format(pack.function_name)
                    )
                elif pack.keywords['side'] != 'tk.LEFT':
                    self.add_error(
                        'You should be packing to the LEFT (got {} instead '
                        'in {})'.format(
                            pack.keywords['side'], pack.function_name
                        )
                    )
                elif len(pack.keywords) > 1:
                    self.add_error(
                        'You only need to provide side as an argument to '
                        'pack (in {})'.format(pack.function_name)
                    )

            # the order does matter with pack!
            # for now, though, let's just make sure they're actually packing
            # different objects
            pack_calls = [p.function_name for p in function_def.calls['pack']]

            if len(pack_calls) != 2:
                self.add_error(
                    'You should call pack exactly twice'
                )
            elif len(set(pack_calls)) != 2:
                self.add_error(
                    'You need to pack both buttons (not just one)'
                )


ANALYSER = Analyser(CodeVisitor)