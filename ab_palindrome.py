import pushdown_automata

pda = pushdown_automata.PushdownAutomata('q0',lambdaSymbol='λ')

pda.addTransition('q0',pda.lambdaSymbol,'a','q0','A')
pda.addTransition('q0',pda.lambdaSymbol,'b','q0','B')
pda.addTransition('q0',pda.lambdaSymbol,pda.lambdaSymbol,'q1',pda.lambdaSymbol)
pda.addTransition('q1','A','a','q1',pda.lambdaSymbol)
pda.addTransition('q1','B','b','q1',pda.lambdaSymbol)
pda.finalStates = {'q0','q1'}

pda.printEval('abba')
