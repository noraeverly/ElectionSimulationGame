import random

def fundraise(app, state, candidate):
    money = app.stateDict[state].availableMoney
    #check that state has money
    if money == 0:
        app.errorMessage = f'{state} has no more money! Try something else.'
        app.turns -= 1
    #can only gain money from states you are leading in
    if app.stateDict[state].demSupport > app.stateDict[state].repSupport:
        if candidate.party == 'D':
            candidate.getMoney(money)
            app.stateDict[state].availableMoney = 0
            app.updateMessage = f'{candidate.name} earned {money}$'
        else:
            app.errorMessage = f'Not your state! Try another one.'
            app.turns -= 1
    elif app.stateDict[state].demSupport < app.stateDict[state].repSupport:
        if candidate.party == 'R':
            candidate.getMoney(money)
            app.stateDict[state].availableMoney = 0
            app.updateMessage = f'{candidate.name} earned {money}$'
        else:
            app.errorMessage = f'Not your state! Try another one.'
            app.turns -= 1
    #no one can fundraise in tied states
    else:
        app.errorMessage = f'Not your state yet! Try something else.'
        app.turns -= 1

def poll(app, state, candidate):
    candidate.money -= 1
    #polled state is now visible
    app.stateDict[state].showing = True
    #message
    app.updateMessage = f'{candidate.name} polled {state}'

def runAds(app, state, candidate, issue):
    candidate.money -= 1
    # issue = pickIssue(app, candidate)
    if issue in app.stateDict[state].hotTopics:
        if candidate.party == 'D':
            app.stateDict[state].influence += 1
        else:
            app.stateDict[state].influence -= 1
        app.updateMessage = f'Successful ad campaign by {candidate.name}!'
    else:
        app.updateMessage = f'The people of {state} did not like {candidate.name}\'s ad campaign.'
    print(state, ':', app.stateDict[state].influence)

def makeSpeech(app, state, candidate, issue):
    candidate.money -= 2
    # issue = pickIssue(app, candidate)
    if issue in app.stateDict[state].hotTopics:
        if candidate.party == 'D':
            app.stateDict[state].influence += 2
        else:
            app.stateDict[state].influence -= 2
        app.updateMessage = f'{candidate.name}\'s speech was a massive success!'
    else:
        app.updateMessage = f'The people of {state} did not like {candidate.name}\'s speech.'
    print(state, ':', app.stateDict[state].influence, 'influence')