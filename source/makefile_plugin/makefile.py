import os, subprocess, time
import pyven.constants

from pyven.plugins.plugin_api.process import Process

from pyven.logging.logger import Logger
from pyven.results.line_logs_parser import LineLogsParser

class Command(Process):

    def __init__(self, cwd, name, workspace, rules, options):
        super(Command, self).__init__(cwd, name)
        self.duration = 0
        self.type = 'makefile'
        self.workspace = workspace
        self.cwd = os.path.join(self.cwd, self.workspace)
        self.rules = rules
        self.options = options
        self.parser = LineLogsParser(error_patterns=['Error', 'error', 'ERROR', 'Erreur', 'erreur', 'ERREUR'],\
                                    error_exceptions=[],\
                                    warning_patterns=['Warning', 'warning', 'WARNING', 'Avertissement', 'avertissement', 'AVERTISSEMENT'],\
                                    warning_exceptions=[])
    
    @Process.error_checks
    def process(self, verbose=False, warning_as_error=False):
        Logger.get().info('Building : ' + self.type + ':' + self.name)
        if os.path.isdir(self.cwd):
            Logger.get().info('Building : ' + self.type + ':' + self.name)
            self.duration, out, err, returncode = self._call_command(self._format_call())
            
            if verbose:
                for line in out.splitlines():
                    Logger.get().info('[' + self.type + ']' + line)
                for line in err.splitlines():
                    Logger.get().info('[' + self.type + ']' + line)
            
            self.parser.parse(out.splitlines() + err.splitlines())
            self.warnings = self.parser.warnings
            
            if returncode != 0:
                self.status = pyven.constants.STATUS[1]
                self.parser.parse(out.splitlines() + err.splitlines())
                self.errors = self.parser.errors
                Logger.get().error('Build failed : ' + self.type + ':' + self.name)
            elif warning_as_error and len(self.warnings) > 0:
                self.status = pyven.constants.STATUS[1]
                Logger.get().error('Build failed : ' + self.type + ':' + self.name)
            else:
                self.status = pyven.constants.STATUS[0]
            return returncode == 0 and (not warning_as_error or len(self.warnings) == 0)
        Logger.get().error('Unknown directory : ' + self.workspace)
        return False
    
    @Process.error_checks
    def clean(self, verbose=False, warning_as_error=False):
        Logger.get().info('Entering directory : ' + self.workspace)
        if os.path.isdir(self.cwd):
            if os.path.isfile(os.path.join(self.cwd, 'Makefile')) or os.path.isfile(os.path.join(self.cwd, 'makefile')):
                Logger.get().info('Cleaning : ' + self.type + ':' + self.name)
                self.duration, out, err, returncode = self._call_command(self._format_call(clean=True))
                
                if verbose:
                    for line in out.splitlines():
                        Logger.get().info('[' + self.type + ']' + line)
                    for line in err.splitlines():
                        Logger.get().info('[' + self.type + ']' + line)
                        
                if returncode != 0:
                    Logger.get().error('Clean failed : ' + self.type + ':' + self.name)
                return returncode == 0
        Logger.get().info('No makefile found')
        self.status = pyven.constants.STATUS[0]
        return True
        
    def report_summary(self):
        return self.report_title()
    
    def report_title(self):
        return self.name
        
    def report_properties(self):
        properties = []
        properties.append(('Workspace', self.workspace))
        properties.append(('Rules', str(self.rules)))
        properties.append(('Duration', str(self.duration) + ' seconds'))
        return properties
        
    def _call_command(self, command):
        tic = time.time()
        out = ''
        err = ''
        try:
            
            sp = subprocess.Popen(command,\
                                  stdin=subprocess.PIPE,\
                                  stdout=subprocess.PIPE,\
                                  stderr=subprocess.PIPE,\
                                  universal_newlines=True,\
                                  cwd=self.cwd,\
                                  shell=pyven.constants.PLATFORM == pyven.constants.PLATFORMS[1])
            out, err = sp.communicate(input='\n')
            returncode = sp.returncode
        except FileNotFoundError as e:
            returncode = 1
            self.errors.append(['Unknown command'])
        toc = time.time()
        return round(toc - tic, 3), out, err, returncode
        
    def _format_call(self, clean=False):
        call = ['make']
        if clean:
            call.append('clean')
        else:
            for option in self.options:
                call.append(option)
            for rule in self.rules:
                call.append(rule)
        Logger.get().info(' '.join(call))
        return call
        