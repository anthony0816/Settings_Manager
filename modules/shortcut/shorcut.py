from pathlib import Path
import json
from modules.logger.logger import log
import sys

class ShortCutController:
    name = 'shortcuts'
    json_name = 'shortcut.json'
        
    def create(self, args):
        create_example = 'wst sc create <script> --name <name>'
        flag_name_allowed = ['--name']
        
        if len(args) < 3:
            log.error(f'example: {create_example}')
            sys.exit(1)
        script = args[0]
        flag_name = args[1] in flag_name_allowed
        name =  args[2]
                
        if not flag_name: 
            log.error(f'unknow flag {flag_name}, allowed: {flag_name_allowed}')
        
        if not self._exist_json_file():
            path = self._get_json_path()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('{}', encoding='utf-8')
        content =  self._load_json_content()
        if not content: 
            content = {self.name: []}
        if self.get_shorcut_or_false(name):
            log.error('One shortcut with same name already exist')
            sys.exit(1)
        content[self.name].append({'name': name, 'script': script})
        self._write_json_content(content)
        log.success('Shortcut created')
        
        
        
    def delete(self, args):
        shorcut_name = args[0]
        sc  = self.get_shorcut_or_false(shorcut_name)
        if not sc:
            log.error('No shorchut with that name')
            sys.exit(1)
        shorcuts = self._load_json_content()[self.name]
        if len(shorcuts) == 0:
            log.error('Nothing to delete, no shorchuts registered')
            sys.exit(1)
        new_shorcuts = []
        for row in shorcuts:
            if row['name'] != sc['name']:
                new_shorcuts.append(row)
        content = {self.name : new_shorcuts}
        self._write_json_content(content)
        log.success('Deleted')
                
        
    def get_shorcut_or_false(self,arg_name):
        if not self._exist_json_file():
            return False
        content = self._load_json_content()
        shorcuts =  content[self.name]
        for sc in shorcuts:
            if sc['name'] == arg_name:
                return sc
        return False 
        
        
        
    def _load_json_content(self):
        return json.loads(self._get_json_path().read_text(encoding='utf-8'))
    
    def _exist_json_file(self):
        return self._get_json_path().exists()
    
    def _get_json_path(self):
        return Path(__file__).resolve().parents[2] / f'{self.json_name}'
    
    def _write_json_content(self,content):
        self._get_json_path().write_text(json.dumps(content), encoding='utf-8')
    
    
scc = ShortCutController()

def handle_shorcut(args):
    
    if len(args) == 0:
        log.error(f'No comando for sc provided')
        sys.exit(1)
        
    command = args[0]
    
    if command == 'create': 
        scc.create(args[1:])
    elif command == 'delete':
        scc.delete(args[1:])
        
def get_sortcut_if_exist(comando_name):
    return scc.get_shorcut_or_false(comando_name)