from pyven.exceptions.parser_exception import ParserException
from pyven.plugins.plugin_api.parser import Parser

from makefile_plugin.makefile import Makefile

class MakefileParser(Parser):
    COUNT = 0
    SINGLETON = None
    
    def __init__(self, cwd):
        MakefileParser.COUNT += 1
        super(MakefileParser, self).__init__(cwd)
    
    def parse(self, node):
        objects = []
        members = self.parse_process(node)
        errors = []
        workspace_node = node.find('workspace')
        if workspace_node is None:
            errors.append('Missing makefile workspace information')
        else:
            workspace = workspace_node.text
        rules_nodes = node.xpath('rules/rule')
        rules = []
        if len(rules_nodes) == 0:
            errors.append('Missing makefile rules information informations')
        else:
            for rule_node in rules_nodes:
                rules.append(rule_node.text)
        options = []
        for option_node in node.xpath('options/option'):
            options.append(option_node.text)
        if len(errors) > 0:
            e = ParserException('')
            e.args = tuple(errors)
            raise e
        objects.append(Makefile(self.cwd, members[0], workspace, rules, options))
        return objects
        
def get(cwd):
    if MakefileParser.COUNT <= 0 or MakefileParser.SINGLETON is None:
        MakefileParser.SINGLETON = MakefileParser(cwd)
    MakefileParser.SINGLETON.cwd = cwd
    return MakefileParser.SINGLETON