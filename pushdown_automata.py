__author__ = 'juaniglesias'
import sys
import machine_state as ms



class PushdownAutomata:
    def __init__(self, q0: str, Q: set=set(), sigma: set=set(),  F: set=set(), gamma: set=set(), lambdaSymbol:str = 'λ'):
        self.states = Q
        self.strAlphabet = sigma
        self.states.add(q0)
        self.startState = q0
        self.finalStates = F
        self.stackAlphabet = gamma
        self.transitions = dict()
        self.stackAlphabet.add(lambdaSymbol)
        self.lambdaSymbol = lambdaSymbol
        self.popKeyLens = []

    def _addTransitionStates(self,currentSymbol: str, popSymbols: tuple, currentState: str, pushSymbols: tuple, nextState: str):
        if currentSymbol not in self.strAlphabet:
            self.strAlphabet.add(currentSymbol)

        for p in popSymbols:
            if p not in self.stackAlphabet:
                self.stackAlphabet.add(p)

        if currentState not in self.states:
            self.states.add(currentState)

        for p in pushSymbols:
            if p not in self.stackAlphabet:
                self.stackAlphabet.add(p)

        if nextState not in self.states:
            self.states.add(nextState)

    def addTransition(self, currentState: str, currentPop, currentSymbol: str, nextState: str, nextPush):

        if not isinstance(currentPop,tuple):
            currentPop = tuple(currentPop)
        if not isinstance(nextPush,tuple):
            nextPush = tuple(nextPush)

        if len(currentPop) not in self.popKeyLens:
            self.popKeyLens.append(len(currentPop))
            self.popKeyLens.sort()

        self._addTransitionStates(currentSymbol, currentPop, currentState, nextPush, nextState)

        if (currentState,currentSymbol,currentPop) not in self.transitions:
            self.transitions[(currentState,currentSymbol,currentPop)] = [(nextState, nextPush)]
        else:
            self.transitions[(currentState,currentSymbol,currentPop)].append((nextState, nextPush))


    def printEval(self, inputString:str):
        eval = self._eval(inputString)
        for i in eval:
            currentState,index,stack, machineState = i
            print('stack: -> ' + str(stack))
            print('current state = '+ currentState)
            print(inputString)
            print(' '*index + '^')
            if machineState == ms.MachineState.accepted:
                print("String accepted!")
            elif machineState == ms.MachineState.rejected:
                print("String rejected!")

    def printTransitionTable(self):
        for k in self.transitions.keys():
            currentState = k[0]
            symbol = k[1]
            pop = ""
            for p in k[2]:
                pop += p + " "
            for t in self.transitions[k]:
                nextState = t[0]
                push = ""
                for p in t[1]:
                    push += p + " "
                print('δ(' + currentState + ',' + symbol + ',' + pop + ') = {[' + nextState + ',' + push + ']}')

    #Print in the format of the book
    def printHomework(self, inputString:str):
        eval = self._eval(inputString)
        firstIter = True
        print(inputString)
        for i in eval:
            currentState,index,stack,machineState = i
            if index < len(inputString):
                remainingString = inputString[index:]
            else:
                remainingString = self.lambdaSymbol
            if firstIter:
                print('   [' + currentState + ',' + remainingString + ',' + stack[-1] + ']')
            else:
                print('  ⊢[' + currentState + ',' + remainingString + ',' + stack[-1] + ']')

            firstIter = False
            if machineState != ms.MachineState.running:
                print()
                firstIter = True

    def convertToUnextended(self):
        unextendedPda = PushdownAutomata(self.startState)
        for k, tlist in self.transitions.items():
            for t in tlist:
                self._unextendAndAddTransition(unextendedPda,t)
        unextendedPda.finalStates = self.finalStates
        return unextendedPda

    #not the prettiest girl at the dance
    def _unextendAndAddTransition(self,pda,transition):
        currentState, symbol, pop, nextState, push = transition
        newCurrentState = currentState

        for p in pop[:-1]:
            newNextState = pda._generateState()
            pda.addTransition(newCurrentState,symbol,p,newNextState,pda.lambdaSymbol)
            newCurrentState = newNextState

        newNextState = nextState if len(push) == 1 else pda._generateState()
        pda.addTransition(newCurrentState,symbol,pop[-1],newNextState,push[0])
        newCurrentState = newNextState
        for p in push[1:-1]:
            newNextState = pda._generateState()
            pda.addTransition(newCurrentState,symbol,pda.lambdaSymbol,newNextState,p)
            newCurrentState = newNextState
        if len(push) > 1:
            pda.addTransition(newCurrentState,symbol,pda.lambdaSymbol,nextState,push[-1])

    def convertToAtomic(self):
        atomicPda = PushdownAutomata(self.startState)
        for k, tlist in self.transitions.items():
            for t in tlist:
                self._atomiziseAndAddTransition(atomicPda, k + t)
        atomicPda.finalStates = self.finalStates
        return atomicPda

    def _atomiziseAndAddTransition(self, pda, transition):
        currentState, symbol, pop, nextState, push = transition
        willAdvanceString = symbol != pda.lambdaSymbol
        willPop = pop != (pda.lambdaSymbol,)
        willPush = push != (pda.lambdaSymbol,)
        transitionNum = 0
        for t in pop + push + (symbol,):
            if t != pda.lambdaSymbol:
                transitionNum += 1
        newCurrentState = currentState

        if transitionNum > 1:
            if willAdvanceString:
                newNextState = pda._generateState()
                pda.addTransition(newCurrentState,pda.lambdaSymbol,symbol,
                                        newNextState,pda.lambdaSymbol)
                newCurrentState = newNextState
            if willPop:
                for p in pop[:-1]:
                    newNextState = pda._generateState()
                    pda.addTransition(newCurrentState,p,pda.lambdaSymbol,
                                        newNextState,pda.lambdaSymbol)
                    newCurrentState = newNextState
                newNextState = pda._generateState() if willPush else nextState
                pda.addTransition(newCurrentState,pop[-1],pda.lambdaSymbol,
                                        newNextState,pda.lambdaSymbol)
                newCurrentState = newNextState
            if willPush:
                for p in push[:-1]:
                    newNextState = pda._generateState()
                    pda.addTransition(newCurrentState, pda.lambdaSymbol, pda.lambdaSymbol,
                                        newNextState, p)
                    newCurrentState = newNextState

                pda.addTransition(newCurrentState, pda.lambdaSymbol, pda.lambdaSymbol,
                                    nextState,push[-1])

        elif transitionNum == 1:
            pda.addTransition(currentState,pop,symbol,nextState,push)

        elif transitionNum == 0:
            for k, tlist in self.transitions.items():
                for t in tlist:
                    if t[0] == currentState:
                        pda._atomiziseAndAddTransition(pda, k + (nextState,) + t[1])

    #return a string in the form of prepend + str(i) where i is the first integer greater than or equal
    #to zero that does not exist as a state
    def _generateState(self, prepend='q'):
        for i in range(sys.maxsize):
            newState = prepend + str(i)
            if  newState not in self.states:
                return newState
        return self._generateState(newState)

    def eval(self,stringOrList):
        eval = self._eval(stringOrList)
        isAccepted = False
        for i in eval:
            machineState = i[3]
            if machineState == ms.MachineState.accepted:
                isAccepted = True
        return isAccepted
    #returns an generator that iterates over a PDA.
    #all non-deterministic transitions are traversed in a depth-first manner
    #each new path begins at the beginning of the string, not at the point at which it forked off from the last path
    def _eval(self, inputString:str, history: list=[]):
        currentState = self.startState
        index = 0
        stack = [self.lambdaSymbol]
        branches = []
        branchHistory = list(history)
        thisHistory = list(history) #copy history to avoid modifying default and passed in lists
        machineState = ms.MachineState.running
        while len(thisHistory) > 0:
            yield (currentState, index, stack, machineState)
            index, currentState = self._doTransition(thisHistory.pop(0),stack,index)

        while machineState == ms.MachineState.running:
            if index < len(inputString):
                symbol = inputString[index]
            elif index == len(inputString):
                symbol = self.lambdaSymbol

            lastState = currentState
            lastIndex = index
            lastStack = list(stack)

            currentTransitions = self._findTransitions(currentState,symbol,stack)

            if lastIndex == len(inputString) and lastStack == [self.lambdaSymbol] and lastState in self.finalStates:
                machineState = ms.MachineState.accepted

            elif currentTransitions == []:
                machineState = ms.MachineState.rejected

            else:
                transition = currentTransitions.pop(0)
                index, currentState = self._doTransition(transition, stack, index)

                for branchTransition in currentTransitions:
                    branches.append(self._eval(inputString, branchHistory + [branchTransition]))
                branchHistory.append(transition)

            yield (lastState, lastIndex, lastStack, machineState)

        for branch in branches:
            yield from branch

    def _doTransition(self, transition, stack, index):
        symbol, pop, currentState, push = transition
        for p in pop:
            if p != self.lambdaSymbol:
                stack.pop()
        for p in push:
            if p != self.lambdaSymbol:
                stack.append(p)
        if symbol != self.lambdaSymbol:
            index += 1
        return (index, currentState)

    def _findTransitions(self,currentState, symbol, stack):
        currentTransitions = []
        lambdaStrTransitions = []
        lambdaStackTransitions = []
        lambdaBothTransitions = []
        for popLen in self.popKeyLens:
            if popLen <= len(stack):
                stackTop = tuple(stack[-popLen:])
                #find non lambda transitions
                if (currentState, symbol, stackTop) in self.transitions and symbol != self.lambdaSymbol and stackTop != (self.lambdaSymbol,):
                    for t in self.transitions[(currentState,symbol,stackTop)]:
                        currentTransitions.append((symbol,stackTop) + t)

                #find lambda transitions that pop stack but don't advance string
                if (currentState, self.lambdaSymbol, stackTop) in self.transitions and stackTop != (self.lambdaSymbol,):
                    for t in self.transitions[(currentState,self.lambdaSymbol,stackTop)]:
                        lambdaStrTransitions.append((self.lambdaSymbol,stackTop) + t)

            #stop looking at the top of the stack when the stack is too small
            else:
                break
        #find lambda transitions that advance string but don't pop stack
        if (currentState, symbol, (self.lambdaSymbol,)) in self.transitions and symbol != self.lambdaSymbol:
            for t in self.transitions[(currentState,symbol,(self.lambdaSymbol,))]:
                lambdaStackTransitions.append((symbol,(self.lambdaSymbol,)) + t)

        #find lambda transitions that don't pop stack or advance string
        if (currentState, self.lambdaSymbol, (self.lambdaSymbol,)) in self.transitions:
            for t in self.transitions[(currentState,self.lambdaSymbol,(self.lambdaSymbol,))]:
                lambdaBothTransitions.append((self.lambdaSymbol,(self.lambdaSymbol,)) + t)

        return currentTransitions + lambdaStackTransitions + lambdaStrTransitions + lambdaBothTransitions
