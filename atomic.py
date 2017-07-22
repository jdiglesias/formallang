__author__ = 'juaniglesias'
'''
This PDA accepts strings that have 'a's followed by 'b's. It demonstrates the convertToAtomic functionality
'''
import pushdown_automata as pda
pushdown = pda.PushdownAutomata('q0')
pushdown.addTransition('q0',pushdown.lambdaSymbol,'a','q0','A')
pushdown.addTransition('q0',('A','A'),'b','q1',pushdown.lambdaSymbol)
pushdown.addTransition('q1',('A','A'),'b','q1',pushdown.lambdaSymbol)
pushdown.finalStates = {'q1'}
atomic = pushdown.convertToAtomic()
atomic.printTransitionTable() # print out new atomic transitions

atomic.printEval("aaaabb") # accept

atomic.printEval("aaaabbaab") # reject
