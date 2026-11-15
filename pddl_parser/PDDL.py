#!/usr/bin/env python
# Four spaces as indentation [no tabs]

# This file is part of PDDL Parser, available at <https://github.com/pucrs-automated-planning/pddl-parser>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import re
from .action import Action

import sys
#sys.path.append("/../")
sys.path.append(r"C:\Users\Mz3ab\Downloads\pddl-parser-update\pddl-parser-update-master")
from search import *

class PDDL_Parser:
    SUPPORTED_REQUIREMENTS = [':strips', ':negative-preconditions', ':typing']

    # -----------------------------------------------
    # Tokens
    # -----------------------------------------------

    def scan_tokens(self, filename):
        with open(filename) as f:
            # Remove single line comments
            str = re.sub(r';.*$', '', f.read(), flags=re.MULTILINE).lower()
        # Tokenize
        stack = []
        list = []
        for t in re.findall(r'[()]|[^\s()]+', str):
            if t == '(':
                stack.append(list)
                list = []
            elif t == ')':
                if stack:
                    li = list
                    list = stack.pop()
                    list.append(li)
                else:
                    raise Exception('Missing open parentheses')
            else:
                list.append(t)
        if stack:
            raise Exception('Missing close parentheses')
        if len(list) != 1:
            raise Exception('Malformed expression')
        return list[0]

    # -----------------------------------------------
    # Parse domain
    # -----------------------------------------------

    def parse_domain(self, domain_filename, requirements=SUPPORTED_REQUIREMENTS):
        tokens = self.scan_tokens(domain_filename)
        if type(tokens) is list and tokens.pop(0) == 'define':
            self.domain_name = 'unknown'
            self.requirements = []
            self.types = {}
            self.objects = {}
            self.actions = []
            self.predicates = {}
            while tokens:
                group = tokens.pop(0)
                t = group.pop(0)
                if t == 'domain':
                    self.domain_name = group[0]
                elif t == ':requirements':
                    for req in group:
                        if req not in requirements:
                            raise Exception('Requirement ' + req + ' not supported')
                    self.requirements = group
                elif t == ':constants':
                    self.parse_objects(group, t)
                elif t == ':predicates':
                    self.parse_predicates(group)
                elif t == ':types':
                    self.parse_types(group)
                elif t == ':action':
                    self.parse_action(group)
                else:
                    self.parse_domain_extended(t, group)
        else:
            raise Exception('File ' + domain_filename + ' does not match domain pattern')

    def parse_domain_extended(self, t, group):
        print(str(t) + ' is not recognized in domain')

    # -----------------------------------------------
    # Parse hierarchy
    # -----------------------------------------------

    def parse_hierarchy(self, group, structure, name, redefine):
        list = []
        while group:
            if redefine and group[0] in structure:
                raise Exception('Redefined supertype of ' + group[0])
            elif group[0] == '-':
                if not list:
                    raise Exception('Unexpected hyphen in ' + name)
                group.pop(0)
                type = group.pop(0)
                if type not in structure:
                    structure[type] = []
                structure[type] += list
                list = []
            else:
                list.append(group.pop(0))
        if list:
            if 'object' not in structure:
                structure['object'] = []
            structure['object'] += list

    # -----------------------------------------------
    # Parse objects
    # -----------------------------------------------

    def parse_objects(self, group, name):
        self.parse_hierarchy(group, self.objects, name, False)

    # -----------------------------------------------
    # Parse types
    # -----------------------------------------------

    def parse_types(self, group):
        self.parse_hierarchy(group, self.types, 'types', True)

    # -----------------------------------------------
    # Parse predicates
    # -----------------------------------------------

    def parse_predicates(self, group):
        for pred in group:
            predicate_name = pred.pop(0)
            if predicate_name in self.predicates:
                raise Exception('Predicate ' + predicate_name + ' redefined')
            arguments = {}
            untyped_variables = []
            while pred:
                t = pred.pop(0)
                if t == '-':
                    if not untyped_variables:
                        raise Exception('Unexpected hyphen in predicates')
                    type = pred.pop(0)
                    while untyped_variables:
                        arguments[untyped_variables.pop(0)] = type
                else:
                    untyped_variables.append(t)
            while untyped_variables:
                arguments[untyped_variables.pop(0)] = 'object'
            self.predicates[predicate_name] = arguments

    # -----------------------------------------------
    # Parse action
    # -----------------------------------------------

    def parse_action(self, group):
        name = group.pop(0)
        if not type(name) is str:
            raise Exception('Action without name definition')
        for act in self.actions:
            if act.name == name:
                raise Exception('Action ' + name + ' redefined')
        parameters = []
        positive_preconditions = []
        negative_preconditions = []
        add_effects = []
        del_effects = []
        extensions = []
        while group:
            t = group.pop(0)
            if t == ':parameters':
                if not type(group) is list:
                    raise Exception('Error with ' + name + ' parameters')
                parameters = []
                untyped_parameters = []
                p = group.pop(0)
                while p:
                    t = p.pop(0)
                    if t == '-':
                        if not untyped_parameters:
                            raise Exception('Unexpected hyphen in ' + name + ' parameters')
                        ptype = p.pop(0)
                        while untyped_parameters:
                            parameters.append([untyped_parameters.pop(0), ptype])
                    else:
                        untyped_parameters.append(t)
                while untyped_parameters:
                    parameters.append([untyped_parameters.pop(0), 'object'])
            elif t == ':precondition':
                self.split_predicates(group.pop(0), positive_preconditions, negative_preconditions, name,
                                      ' preconditions')
            elif t == ':effect':
                self.split_predicates(group.pop(0), add_effects, del_effects, name, ' effects')
            else:
                group.insert(0, t)
                extensions.append(group)
        action = Action(name, parameters, positive_preconditions, negative_preconditions, add_effects, del_effects)
        self.parse_action_extended(action, extensions)
        self.actions.append(action)

    def parse_action_extended(self, action, group):
        while group:
            t = group.pop(0)
            print(str(t) + ' is not recognized in action ' + action.name)

    # -----------------------------------------------
    # Parse problem
    # -----------------------------------------------

    def parse_problem(self, problem_filename):
        def frozenset_of_tuples(data):
            return frozenset([tuple(t) for t in data])

        tokens = self.scan_tokens(problem_filename)
        if type(tokens) is list and tokens.pop(0) == 'define':
            self.problem_name = 'unknown'
            self.state = frozenset()
            self.positive_goals = frozenset()
            self.negative_goals = frozenset()
            while tokens:
                group = tokens.pop(0)
                t = group.pop(0)
                if t == 'problem':
                    self.problem_name = group[0]
                elif t == ':domain':
                    if self.domain_name != group[0]:
                        raise Exception('Different domain specified in problem file')
                elif t == ':requirements':
                    pass  # Ignore requirements in problem, parse them in the domain
                elif t == ':objects':
                    self.parse_objects(group, t)
                elif t == ':init':
                    self.state = frozenset_of_tuples(group)
                elif t == ':goal':
                    positive_goals = []
                    negative_goals = []
                    self.split_predicates(group[0], positive_goals, negative_goals, '', 'goals')
                    self.positive_goals = frozenset_of_tuples(positive_goals)
                    self.negative_goals = frozenset_of_tuples(negative_goals)
                else:
                    self.parse_problem_extended(t, group)
        else:
            raise Exception('File ' + problem_filename + ' does not match problem pattern')

    def parse_problem_extended(self, t, group):
        print(str(t) + ' is not recognized in problem')

    # -----------------------------------------------
    # Split predicates
    # -----------------------------------------------

    def split_predicates(self, group, positive, negative, name, part):
        if not type(group) is list:
            raise Exception('Error with ' + name + part)
        if group:
            if group[0] == 'and':
                group.pop(0)
            else:
                group = [group]
            for predicate in group:
                if predicate[0] == 'not':
                    if len(predicate) != 2:
                        raise Exception('Unexpected not in ' + name + part)
                    negative.append(predicate[-1])
                else:
                    positive.append(predicate)

def create_connections(state):
  connections = []
  state = [list(i) for i in state]
  for i in state:
    if len(i) > 2:
      connections.append((i[1], i[2], 1))
  return connections

def create_unique(connections):
  y = set()
  lst = []
  for i in connections:
    t = tuple(sorted(i, key=str))
    if t not in y:
         y.add(t)
         lst.append(i)
  return lst

def create_goal_state(positive_goals):
  goal_state = []
  positive_state = [list(i) for i in positive_goals]
  for i in positive_state:
    goal_state.append(i[1])
  goal_state = list(set(goal_state))
  return goal_state

# only use unique connections
def create_locations(objects, unique_connections):
  cities = objects['position']
  locations_list = []
  locations = {}
  for i in cities:
    for c in unique_connections:
      if i == c[0] or i == c[1]:
        locations_list.append(c[2])
      locations[i] = locations_list
    locations_list = []
  return locations

def create_heuristics(objects):
  cities_list = objects['position']
  costs_list = [1] * len(cities_list)
  h_dict = dict(zip(cities_list,costs_list))
  return h_dict

def find_at_city(state):
  st = [list(i) for i in state]
  at_city = [x for x in st if x[0] == 'at'][0][1]
  return at_city

def reverse_goal_state(positive_goals):
  goal_state = []
  positive_state = [list(i) for i in positive_goals]
  for i in positive_state:
    goal_state.append(i[1])
  goal_state = list(set(goal_state))
  goal_state.reverse()
  return goal_state
