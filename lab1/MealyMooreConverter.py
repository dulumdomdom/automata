import csv
import argparse

STATE_PREFIX = 'R'
OUTPUT_SEPARATOR = '/'
TRANSFORM_MEALY_TO_MOORE = 'mealy-to-moore'
TRANSFORM_MOORE_TO_MEALY = 'moore-to-mealy'


def saveToCsv(fileName, data, delimiter=';'):
    with open(fileName, 'w', newline='', encoding='ISO-8859-1') as file:
        writer = csv.writer(file, delimiter=delimiter)
        writer.writerows(data)


def loadMealyFromCsv(fileName, delimiter=';'):
    with open(fileName, 'r', encoding='ISO-8859-1') as file:
        reader = csv.reader(file, delimiter=delimiter)
        data = []

        for row in reader:
            data.append(row)

        mealyStates = []
        for index, state in enumerate(data[0]):
            if index == 0:
                continue
            mealyStates.append(state.strip())

        stateOutputs = {}
        transitionsByInput = {}
        
        for index, transitions in enumerate(data):
            if index == 0:
                continue

            inputValue = transitions[0].strip()

            for index2, transition in enumerate(transitions[1:]):
                state_output = transition.strip().split(OUTPUT_SEPARATOR)

                # Проверка на наличие двух элементов
                if len(state_output) < 2:
                    print(f"Warning: Transition '{transition}' does not have enough elements.")
                    continue  # Пропускаем этот переход

                state = state_output[0]
                output = state_output[1]

                if state not in stateOutputs:
                    stateOutputs[state] = set()
                stateOutputs[state].add(output)

                if inputValue not in transitionsByInput:
                    transitionsByInput[inputValue] = {}

                mealyStateKey = mealyStates[index2]  # Правильный индекс состояния
                transitionsByInput[inputValue][mealyStateKey] = f"{state}{OUTPUT_SEPARATOR}{output}"

        return mealyStates, stateOutputs, transitionsByInput


def loadMooreFromCsv(fileName, delimiter=';'):
    with open(fileName, 'r', encoding='ISO-8859-1') as file:
        reader = csv.reader(file, delimiter=delimiter)
        data = []

        for row in reader:
            data.append(row)

        outputs = []
        for index, output in enumerate(data[0]):
            if index == 0:
                continue
            outputs.append(output.strip())

        mooreStates = []
        for index, mooreState in enumerate(data[1]):
            if index == 0:
                continue
            mooreStates.append(mooreState.strip())

        stateOutputs = {}
        for index, mooreState in enumerate(mooreStates):
            output = outputs[index]
            stateOutputs[mooreState] = output

        transitionsByInput = {}
        for index, transitions in enumerate(data):
            if index <= 1:
                continue

            inputValue = transitions[0].strip()

            for index2, transition in enumerate(transitions[1:]):
                state = transition.strip()
                output = stateOutputs[state]

                if inputValue not in transitionsByInput:
                    transitionsByInput[inputValue] = {}

                mooreStateKey = list(stateOutputs.keys())[index2]
                transitionsByInput[inputValue][mooreStateKey] = f"{state}{OUTPUT_SEPARATOR}{output}"

        return stateOutputs, transitionsByInput


def convertMealyToMoore(inputFileName, outputFileName):
    mealyStates, stateOutputs, transitionsByInput = loadMealyFromCsv(inputFileName)
    transformedStates = {}

    sortedStateOutputs = dict(
        sorted(stateOutputs.items(),
               key=lambda item: mealyStates.index(item[0]) if item[0] in mealyStates else float('inf')))
    for mealyState, outputs in sortedStateOutputs.items():
        sortedStateOutputs[mealyState] = sorted(outputs)

    for mealyState in mealyStates:
        if mealyState in sortedStateOutputs:
            for output in sortedStateOutputs[mealyState]:
                transitionKey = f"{mealyState}{OUTPUT_SEPARATOR}{output}"
                transformedStates[transitionKey] = f"{STATE_PREFIX}{len(transformedStates)}"
        else:
            transformedStates[mealyState] = f"{STATE_PREFIX}{len(transformedStates)}"

    outputsRow = ['']
    statesRow = ['']
    for mealyState in mealyStates:
        if mealyState in sortedStateOutputs:
            for output in sortedStateOutputs[mealyState]:
                outputsRow.append(output)
                statesRow.append(transformedStates[f"{mealyState}{OUTPUT_SEPARATOR}{output}"])
        else:
            outputsRow.append('')
            statesRow.append(transformedStates[mealyState])

    transitionRows = []
    for inputValue, transitions in transitionsByInput.items():
        row = [inputValue]

        for currentState in transitions:
            nextTransitionKey = transitionsByInput[inputValue][currentState]

            countOutputs = len(stateOutputs.get(currentState, [1]))
            for i in range(countOutputs):
                row.append(transformedStates[nextTransitionKey])

        transitionRows.append(row)

    finalData = [outputsRow, statesRow]
    finalData.extend(transitionRows)

    saveToCsv(outputFileName, finalData)


def convertMooreToMealy(inputFileName, outputFileName):
    stateOutputs, transitionsByInput = loadMooreFromCsv(inputFileName)

    statesRow = ['']
    for mooreState in stateOutputs.keys():
        statesRow.append(mooreState)

    transitionRows = []
    for inputValue, transitions in transitionsByInput.items():
        row = [inputValue]

        for currentState in transitions:
            nextTransitionKey = transitionsByInput[inputValue][currentState]
            row.append(nextTransitionKey)

        transitionRows.append(row)

    finalData = [statesRow]
    finalData.extend(transitionRows)

    saveToCsv(outputFileName, finalData)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CSV State Machine Converter.')
    parser.add_argument('conversionType', type=str, help='Conversion type (mealy-to-moore or moore-to-mealy)')
    parser.add_argument('inputFile', type=str, help='Input CSV file')
    parser.add_argument('outputFile', type=str, help='Output CSV file')

    args = parser.parse_args()

    if args.conversionType == TRANSFORM_MEALY_TO_MOORE:
        convertMealyToMoore(args.inputFile, args.outputFile)
    elif args.conversionType == TRANSFORM_MOORE_TO_MEALY:
        convertMooreToMealy(args.inputFile, args.outputFile)
    else:
        print('Invalid conversion type specified.')
