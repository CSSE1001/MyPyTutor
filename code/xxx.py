#{TestCode}#
#{global}#
import compiler
class CodeVisitor:
    def __init__(self):
        self.argnum = None
        self.in_defn = False
        self.has_try = False
        self.has_except = False
        self.has_try_return = False
        self.has_except_return = False
        self.in_try = False
        self.in_except = False
        self.callf = False
        
    def visitFunction(self,t):
        if t.name == 'catchException':
            self.in_defn = True
            self.argnum = len(t.argnames)
            for n in t.getChildNodes():
                compiler.walk(n, self)

    def visitTryExcept(self,t):
        if self.in_defn:
            self.has_try = True
            self.in_try = True
            self.in_except = False
            for n in t.getChildNodes():
                compiler.walk(n, self)
                self.in_try = True
                self.in_except = False
            self.in_except = False
              

    def visitName(self,t):
        if self.has_try:
            if t.name == 'Exception':
                self.has_except = True
        
    def visitCallFunc(self,t):
        if self.has_try:
            if t.node.name == 'f':
                self.callf = True
           
    def visitReturn(self,t):
        if self.in_try:
            self.has_try_return = True
        if self.in_except:
            self.has_except_return = True
        


#{test}#
#{code}#
ast = compiler.parse(user_text)
visitor = CodeVisitor()
compiler.walk(ast, visitor)

if not visitor.in_defn:
    print_error('Wrong: no definition of catchException')
elif visitor.argnum != 0:
    print_error('Wrong: catchException should not have arguments')
elif not visitor.callf:
    print_error('Wrong: you need to call f inside the definition of catchException')
elif not visitor.has_try:
    print_error('Wrong: you are not using a try/except statement.')
elif not visitor.has_except:
    print_error('Wrong: you should be using except Exception,e'
elif not visitor.has_try_return:
    print_warning('You probably need a return statement in the try part')
elif not visitor.has_except_return:
    print_warning('You probably need a return statement in the except part')
                
#{test}#

#{init}#
x=1
def f():
    1/x
#{code}#
try:
    result = catchException()
    if result != "No exception raised":
        print_error("Wrong: the correct result is 'No exception raised'\nyou got %s" % repr(result))
except Exception, e:
    print_error("Wrong: You did not trap the exception '%s'" % str(e))


#{test}#

#{init}#
x=0
def f():
    1/x
#{code}#
try:
    result = catchException()
    if result != "integer division or modulo by zero":
        print_error("Wrong: the correct result is 'integer division or modulo by zero'\nyou got %s" % repr(result))
    else:
        correct()
except exception, e:
    print_error("Wrong: You did not trap the exception '%s'" % str(e))


