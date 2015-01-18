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

            btn_calls = function_def.calls['Button']
            pack_calls = function_def.calls['pack']

            for n, btn in enumerate(btn_calls):
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

            for pack in pack_calls:
                if pack.args:
                    self.add_error(
                        'You should not give positional arguments to pack'
                    )

                if 'side' not in pack.keywords:
                    self.add_error(
                        'You need to provide side as a keyword argument to '
                        'pack (in {})'.format(pack.function_name)
                    )
                elif pack.keywords['side'] != 'tk.TOP':
                    self.add_error(
                        'You appear to be using the wrong value for side '
                        '(in {})'.format(pack.function_name)
                    )

                if 'anchor' not in pack.keywords:
                    self.add_error(
                        'You need to make sure that the buttons appear on top '
                        'of each other on the left of the frame'
                    )
                elif pack.keywords['anchor'] != 'tk.W':
                    self.add_error(
                        'You appear to be using the wrong value for anchor '
                        '(in {})'.format(pack.function_name)
                    )

            # first, make sure that they're packing twice
            if len(pack_calls) != 2:
                self.add_error(
                    'You should call pack exactly twice'
                )
            elif len(set(pack_calls)) != 2:
                self.add_error(
                    'You need to pack both buttons (not just one)'
                )
            else:
                # now, check that they're packing both in the right order
                for btn, pack in zip(btn_calls, pack_calls):
                    # (these are framework asserts, not student code asserts)
                    assert btn in function_def.assigned_values
                    assert len(function_def.assigned_values[btn]) > 0
                    btn_id = function_def.assigned_values[btn][0]

                    if not pack.function_name.startswith(btn_id):
                        self.add_error(
                            'Make sure you pack the buttons in the correct '
                            'order: expected {}.pack but got {}'.format(
                                btn_id, pack.function_name
                            )
                        )

                # now we can deal with the individual pack args that we needed
                pack1, pack2 = pack_calls

                if 'ipady' in pack1.keywords:
                    self.add_error(
                        'You need to add external padding to the second '
                        'button, not internal padding'
                    )
                if 'pady' not in pack1.keywords:
                    self.add_error(
                        'You need to add space above and below the first '
                        'button (in {})'.format(pack1.function_name)
                    )
                elif pack1.keywords['pady'] != 20:
                    self.add_error(
                        'You must add exactly 20 pixels of space above and '
                        'below the first button'
                    )

                if 'padx' in pack2.keywords:
                    self.add_error(
                        'You need to add internal padding to the second '
                        'button, not external padding'
                    )
                if 'ipadx' not in pack2.keywords:
                    self.add_error(
                        'You need to add internal space to the left and the '
                        'right of the second button (in {})'.format(
                            pack2.function_name
                        )
                    )
                elif pack2.keywords['ipadx'] != 20:
                    self.add_error(
                        'You must add exactly 20 pixels of internal space to '
                        'the left and right of the second button'
                    )

                # because errors are displayed in order, we only want to deal
                # with the number of keyword args here, after more specific
                # error messages have been provided
                for pack in pack_calls:
                    if len(pack.keywords) > 3:
                        self.add_error(
                            "You don't need that many arguments to pack. "
                            "You gave: {}".format(pack)
                        )


ANALYSER = Analyser(CodeVisitor)