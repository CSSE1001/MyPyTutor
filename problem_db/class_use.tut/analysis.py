class CodeVisitor(TutorialNodeVisitor):
    def __init__(self):
        super().__init__()

        # print_friend_info
        self._pfo_name_id = None
        self._pfo_age_id = None
        self._pfo_other_id = None
        self._pfo_other_name_id = None

        self.pfo_prints_name = False
        self.pfo_prints_age = False

        self.pfo_uses_get_friend = False
        self.pfo_prints_other_name = False

        self.pfo_has_branch = False
        self.pfo_branch_checks_friend = False

        # create_fry
        self.cf_creates_instance = False

        # make_friends
        self.mf_sets_friend_one = False
        self.mf_sets_friend_two = False

    def visit_Call(self, node):
        super().visit_Call(node)

        function_name = TutorialNodeVisitor.identifier(node.func)
        arg_ids = TutorialNodeVisitor.involved_identifiers(
            *node.args
        )

        if self._current_function == 'print_friend_info' \
                and self.functions['print_friend_info'].args[0] is not None:
            friend_arg_id = self.functions['print_friend_info'].args[0]

            # main logic: checking that we're printing
            if function_name == 'print':
                # first case: printing the friend's name
                if self._pfo_name_id in arg_ids \
                        or (friend_arg_id in arg_ids \
                            and 'get_name' in arg_ids):
                    self.pfo_prints_name = True

                # second case: printing the friend's age
                if self._pfo_age_id in arg_ids \
                        or (friend_arg_id in arg_ids and 'get_age' in arg_ids):
                    self.pfo_prints_age = True

                # third case: printing name of the other guy
                if self._pfo_other_name_id in arg_ids \
                        or (self._pfo_other_id in arg_ids \
                            and 'get_name' in arg_ids) \
                        or (friend_arg_id in arg_ids \
                            and 'get_friend' in arg_ids \
                            and 'get_name' in arg_ids):
                    self.pfo_prints_other_name = True

            elif function_name == 'get_friend':
                self.pfo_uses_get_friend = True

        elif self._current_function == 'create_fry':
            if function_name == 'Person':
                self.cf_creates_instance = True

        elif self._current_function == 'make_friends' \
                and len(self.functions['make_friends'].args) == 2:
            friend_one_id, friend_two_id = self.functions['make_friends'].args

            if function_name == 'set_friend' and friend_one_id in arg_ids:
                self.mf_sets_friend_one = True
            elif function_name == 'set_friend' and friend_two_id in arg_ids:
                self.mf_sets_friend_two = True

    def visit_Assign(self, node):
        super().visit_Assign(node)

        if self._current_function == 'print_friend_info' \
                and self.functions['print_friend_info'].args[0] is not None:
            # supplementary logic: getting names, ages, friends etc
            friend_arg_id = self.functions['print_friend_info'].args[0]

            value_ids = TutorialNodeVisitor.involved_identifiers(
                node.value
            )
            target_identifier = TutorialNodeVisitor.involved_identifiers(
                *node.targets
            )[0]

            # friend's name
            if friend_arg_id in value_ids and 'get_name' in value_ids:
                self._pfo_name_id = target_identifier

            # friend's age
            if friend_arg_id in value_ids and 'get_age' in value_ids:
                self._pfo_age_id = target_identifier

            # other friend
            if friend_arg_id in value_ids and 'get_friend' in value_ids:
                self._pfo_other_id = target_identifier

            # other friend's name
            if self._pfo_other_id in value_ids and 'get_name' in value_ids:
                self._pfo_other_name_id = target_identifier

    def visit_If(self, node):
        super().visit_If(node)

        if self._current_function == 'print_friend_info' \
                and self.functions['print_friend_info'].args[0] is not None:
            self.pfo_has_branch = True

            test_ids = TutorialNodeVisitor.involved_identifiers(node)
            friend_arg_id = self.functions['print_friend_info'].args[0]

            if self._pfo_other_id in test_ids \
                    or (friend_arg_id in test_ids \
                        and 'get_friend' in test_ids):
                self.pfo_branch_checks_friend = True


class PersonAnalyser(CodeAnalyser):
    def _analyse(self):
        num_expected_args = {
            'print_friend_info': 1,
            'create_fry': 0,
            'make_friends': 2,
        }

        # check functions are defined and accept the right number of args
        for function_name, argc in num_expected_args.items():
            function = self.visitor.functions[function_name]

            if not function.is_defined:
                self.add_error('You need to define {}'.format(function_name))
            elif len(function.args) != argc:
                self.add_error('{} should accept exactly {} args'.format(
                    function_name, argc
                ))

        # print_friend_info
        if not self.visitor.pfo_prints_name:
            self.add_error(
                "You need to print the person's name in print_friend_info"
            )
        if not self.visitor.pfo_prints_age:
            self.add_error(
                "You need to print the person's age in print_friend_info"
            )

        if not self.visitor.pfo_uses_get_friend:
            self.add_error(
                "You need to use get_friend to get the friend in "
                "print_friend_info"
            )
        if not self.visitor.pfo_prints_other_name:
            self.add_error(
                "You need to print the name of the person's friend in "
                "print_friend_info"
            )

        if not self.visitor.pfo_has_branch:
            self.add_error(
                "print_friend_info should only print 'Friends with' if the "
                "person has a friend"
            )
        if not self.visitor.pfo_branch_checks_friend:
            self.add_error(
                "Your If statement in print_friend_info should check if the "
                "friend is None"
            )

        # create_fry
        if not self.visitor.cf_creates_instance:
            self.add_error('create_fry should use Person')

        # make_friends
        mf_sets_friends = self.visitor.mf_sets_friend_one \
                or self.visitor.mf_sets_friend_two
        mf_sets_both_friends = self.visitor.mf_sets_friend_one \
                and self.visitor.mf_sets_friend_two

        if not mf_sets_friends:
            self.add_error('You need to use set_friend in make_friends')
        elif not mf_sets_both_friends:
            self.add_error(
                'You need to set each person as a friend of the other'
            )


ANALYSER = PersonAnalyser(CodeVisitor)
