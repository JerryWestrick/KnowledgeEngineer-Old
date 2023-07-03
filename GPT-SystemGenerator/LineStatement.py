import glob

from lark import Lark, Transformer
import colors
from logger import Logger

LineStatement_Grammar = r"""
    ?start: "." statement 
        
    ?statement: role_statement
            | include_statement
            | text_block_statement
            | foreach_statement
            | endfor_statement
            
    ?role_statement: ml_role_statement 
                   | sl_role_statement 
    
    ml_role_statement: role_name 
    
    sl_role_statement: role_name rest_of_line
    
    role_name: role_name2
        
    role_name2: "system"     -> system
             | "user"        -> user
             | "assistant"   -> assistant
             | "function"    -> function
        
    include_statement: "include" rest_of_line

    text_block_statement: "text_block" rest_of_line
    
    foreach_statement: "foreach" VAR "in" MEMORY_NAME
     
    endfor_statement:  "endfor"
    
    rest_of_line: ENDOFLINE
    
    VAR.1: /[\w\d]+/ 
    
    ENDOFLINE: /[^\n]+/
    
    MEMORY_NAME: /[\w\d][\w\d\/]*/
    
    %ignore " "
    """


class MyTransformer(Transformer):

    @staticmethod
    def start(statements):
        Logger.log('LARK', f"start({statements})")
        return statements

    @staticmethod
    def statement(statement):
        Logger.log('LARK', f"statement({statement})")
        return statement

    @staticmethod
    def role_statement(statement):
        Logger.log('LARK', f"role_statement({statement})")
        return statement

    @staticmethod
    def ml_role_statement(statement):
        # Logger.log('LARK', f"ml_role_statement({statement})")
        return {'statement': 'ml_role_statement', 'role': statement[0]}

    @staticmethod
    def sl_role_statement(statement):
        # Logger.log('LARK', f"sl_role_statement({statement})")
        return {'statement': 'sl_role_statement', 'role': statement[0], 'content': statement[1].strip()}

    @staticmethod
    def role_name(statement):
        # Logger.log('LARK', f"role_name({statement})")
        return statement[0].data

    @staticmethod
    def include_statement(statement):
        # Logger.log('LARK', f"include_statement({statement})")
        return {'statement': 'include_statement', 'name': statement[0].strip()}

    @staticmethod
    def text_block_statement(statement):
        # Logger.log('LARK', f"text_block_statement({statement})")
        return {'statement': 'text_block_statement', 'name': statement[0].strip()}

    @staticmethod
    def foreach_statement(statement):
        Logger.log('LARK', f"foreach_statement({statement})")
        return statement

    @staticmethod
    def endfor_statement(statement):
        Logger.log('LARK', f"endfor_statement({statement})")
        return statement

    @staticmethod
    def rest_of_line(statement):
        # Logger.log('LARK', f"rest_of_line({statement})")
        return statement[0]

    @staticmethod
    def VAR(statement):
        Logger.log('LARK', f"VAR({statement})")
        return statement

    @staticmethod
    def ENDOFLINE(statement):
        # Logger.log('LARK', f"ENDOFLINE({statement})")
        return statement.value

    @staticmethod
    def MEMORY_NAME(statement):
        Logger.log('LARK', f"MEMORY_NAME({statement})")
        return statement

    @staticmethod
    def DOT(statement):
        Logger.log('LARK', f"DOT({statement})")
        return statement


class Compiler:
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
            elif len(result) == 1:
                statements.append({'statement': 'sl_role_statement', 'role': 'user', 'content': result_line})

            elif len(result) > 1:
                last = statements[-1]
                if last['statement'] == 'ml_role_statement':
                    last['content'] = result_line
                    last['statement'] = 'sl_role_statement'
                else:
                    statements.append({'statement': 'literal_line', 'content': result_line})

        # Logger.log('STEP', "statements:")
        # for stmt in statements:
        #     Logger.log('STEP', stmt)

        return statements

    def execute(self, statements):
        messages = []
        role = 'user'
        literal_line_content = ''

        for statement in statements:
            keyword = statement['statement']
            if keyword != 'literal_line' and literal_line_content != '':
                # write the literal_line_content to messages
                messages.append(
                    {'role': role, 'content': literal_line_content}
                )
                role = None
                literal_line_content = ''
                # continue with this statement

            if keyword == 'literal_line':
                if 'line' in statement:
                    literal_line_content = f"{literal_line_content}\n{statement['line']}"
                # will be written later

            elif keyword == 'ml_role_statement':
                role = statement['role']

            elif keyword == 'sl_role_statement':
                messages.append(
                    {'role': statement['role'], 'content': statement['content']}
                )

            elif keyword == 'include_statement':
                msgs = self.db[statement['name']]
                messages.extend(msgs)

            elif keyword == 'text_block_statement':
                # Check for file-globing
                if '*' in statement['name']:
                    files = self.db.glob_files(statement['name'])
                else:
                    files = [statement['name']]

                for file in files:
                    # Logger.log('STEP',f"{colors.INFO}- {file}")
                    # assumes only one msg is returned
                    msgs = self.db[file]
                    msg = msgs[0]
                    parts = file.split('/')
                    content = f"{parts[-1]}\n```\n{msg['content']}\n```"
                    messages.append({"role": msg["role"], "content": content})

                continue  # next line

            # elif keyword == 'foreach':
            #     pass
            # elif keyword == 'endfor':
            #     pass
            else:
                errmsg = f"Invalid instruction [{keyword}] "
                Logger.log('STEP', f"{colors.ERROR}{errmsg}")
                raise Exception(errmsg)

        if role is not None and literal_line_content != '':
            messages.append(
                {'role': role, 'content': literal_line_content}
            )

        return messages

#
# Well that was one tough SOB
#
