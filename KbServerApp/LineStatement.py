import glob

from lark import Lark, Transformer
# import KbServerApp.colors
# from KbServerApp import colors
# from KbServerApp.logger import GptLogger as Logger
from twisted.logger import Logger

LineStatement_Grammar = r"""
    ?start: "." statement 
        
    ?statement: role_statement
            | include_statement
            | text_block_statement
            | exec_statement
            
    role_statement: role_name 
    
    sl_role_statement: role_name rest_of_line
    
    role_name: "system"     -> system
             | "user"        -> user
             | "assistant"   -> assistant
             | "function"    -> function
        
    include_statement: "include" rest_of_line

    text_block_statement: "text_block" rest_of_line
    
    exec_statement:  "exec"
    
    rest_of_line: ENDOFLINE
    
    VAR.1: /[\w\d]+/ 
    
    ENDOFLINE: /[^\n]+/
    
    MEMORY_NAME: /[\w\d][\w\d\/]*/
    
    %ignore " "
    """


class MyTransformer(Transformer):
    # Class Variables
    log = Logger(namespace='LARK Transformer')

    @staticmethod
    def start(statements):
        # MyTransformer.log('LARK', f"start({statements})")
        return statements

    @staticmethod
    def statement(statement):
        # MyTransformer.log('LARK', f"statement({statement})")
        return statement

    @staticmethod
    def role_statement(statement):
        # MyTransformer.log.info("role_statement({statement})", statement=statement)
        return {'statement': 'set_role', 'role': statement[0].data}

    @staticmethod
    def role_name(statement):
        # MyTransformer.log.info(f"role_name({statement})")
        return statement[0].data

    @staticmethod
    def include_statement(statement):
        # MyTransformer.log.info(f"include_statement({statement})")
        return {'statement': 'include_statement', 'name': statement[0].strip()}

    @staticmethod
    def text_block_statement(statement):
        # MyTransformer.log.info(f"text_block_statement({statement})")
        return {'statement': 'text_block_statement', 'name': statement[0].strip()}

    @staticmethod
    def exec_statement(statement):
        # MyTransformer.log.info(f"exec_statement({statement})")
        return {'statement': 'exec_statement'}

    @staticmethod
    def rest_of_line(statement):
        # MyTransformer.log.info(f"rest_of_line({statement})")
        return statement[0]

    @staticmethod
    def VAR(statement):
        # MyTransformer.log.info(f"VAR({statement})")
        return statement

    @staticmethod
    def ENDOFLINE(statement):
        # MyTransformer.log.info(f"ENDOFLINE({statement})")
        return statement.value

    @staticmethod
    def MEMORY_NAME(statement):
        # MyTransformer.log.info(f"MEMORY_NAME({statement})")
        return statement

    @staticmethod
    def DOT(statement):
        # MyTransformer.log.info(f"DOT({statement})")
        return statement


class Compiler:
    log = Logger(namespace='LineStmt Compiler')

    def __init__(self, db=None):
        self.db = db
        self.parser = Lark(LineStatement_Grammar, start='start')
        self.transformer = MyTransformer()
        pass

    def compile(self, lines: [str]):
        result = []

        a_line = ''
        for line in lines:
            if line.startswith("."):
                if a_line != '':
                    result.append(a_line)
                    a_line = ''

                result.append(line)
            else:
                a_line = f"{a_line}\n{line}"

        if a_line != '':
            result.append(a_line)

        # Logger.log('STEP', f"result: {result}")

        statements = []
        for result_line in result:
            if result_line.startswith("."):
                tree = self.parser.parse(result_line.strip())
                statement = MyTransformer().transform(tree)
                statements.append(statement)
            else:
                statements.append({'statement': 'literal_line', 'content': result_line})

        # self.log.info("statements:")
        # for stmt in statements:
        #     self.log.info("{stmt}", stmt=stmt)

        return statements

    def execute(self, statements):
        calls = []
        messages = []
        stmts: dict[str, str] = {'system': '', 'user': ''}
        role = 'user'
        literal_line_content = ''

        for statement in statements:
            keyword = statement['statement']

            if keyword == 'literal_line':
                c = statement['content']
                new_value = f"{stmts[role]}\n{c}"
                stmts[role] = new_value.strip()     # Drop Leading and Trailing WhiteSpace

            elif keyword == 'set_role':
                role = statement['role']

            elif keyword == 'include_statement':
                msgs = self.db[statement['name']]
                for msg in msgs[:-1]:
                    stmts[msg['role']] = f"{stmts[msg['role']]}\n{msg['content']}"

            elif keyword == 'text_block_statement':
                # print(f"in {keyword}")
                # Check for file-globing
                if '*' in statement['name']:
                    files = self.db.glob_files(statement['name'])
                else:
                    files = [statement['name']]

                for file in files:
                    # print(f"in {file}")
                    # Logger.log('STEP',f"{colors.INFO}- {file}")
                    # assumes only one msg is returned
                    msgs = self.db[file]
                    # print(f"in {file} 2")
                    msg = msgs[0]
                    # print(f"in {file} 3")
                    # parts = file.split('/')
                    content = f"\n```filename={file}\n{msg['content']}\n```"
                    stmts[role] += content

                # print(f"out {keyword}")
                continue  # next line

            elif keyword == 'exec_statement':
                # self.log.info("In Execute Statement: {statement}", statement=statement)
                if stmts['system'] != '':
                    messages.append({'role': 'system', 'content': stmts['system']})
                messages.append({'role': 'user', 'content': stmts['user']})
                messages.append({"role": "exec", "content": "Execute Call AI Before Continuing"})
                stmts = {'system': '', 'user': ''}
            else:
                errmsg = f"Invalid instruction [{keyword}] "
                self.log.error("{errmsg}", errmsg=errmsg)
                raise Exception(f"{errmsg}")

        if stmts['system'] != '':
            messages.append({'role': 'system', 'content': stmts['system'].strip()})

        if stmts['user'] != '':
            messages.append({'role': 'user', 'content': stmts['user'].strip()})

        if messages[-1]['role'] != 'exec':
            messages.append({"role": "exec", "content": "Default Execute Call AI at end"})
        return messages

#
# Okay That got alot Easier
#
