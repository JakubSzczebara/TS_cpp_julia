using DelimitedFiles
using Dates

# Struktura przechowująca wyniki algorytmu
struct AlgorithmResult
    time::Int
    cost::Float64
    path::Vector{Int}
end

# Obliczenie kosztu sciezki
function calculateCost(path::Vector{Int}, graphMatrix::Array{Float64,2})
    totalCost = 0.0
    for i in 1:length(path)-1
        totalCost += graphMatrix[path[i], path[i+1]] 
    end
    totalCost += graphMatrix[path[end], path[1]]
    return totalCost
end

# Generowanie listy sasiednich rozwiazan
function generateSimilarPaths(currentPath::Vector{Int})
    similarPaths = Vector{Vector{Int}}()
    for i = 1:length(currentPath), j = i+1:length(currentPath)
            newPath = copy(currentPath)
            swap!(newPath, i, j)
            push!(similarPaths, newPath)
    end
    return similarPaths
end

# Zamiana wartości w wektorze
function swap!(arr::Vector{Int}, i::Int, j::Int)
    temp = arr[i]
    arr[i] = arr[j]
    arr[j] = temp
end

function tabuSearch(graphMatrix::Array{Float64,2})
    # Inicjalizacja zmiennych algorytmu
    resultPath = Vector{Int}()
    currentPath = Vector{Int}()
    tabuList = Vector{Vector{Int}}()
    resultCost = Inf
    numCities = size(graphMatrix, 1)
    maxIterations = 50000
    maxTabuListSize = numCities * 2

    
    
    # Tworzenie rozwiazania poczatkowego
    line = readlines("startPath.txt")[1]
    currentPath = parse.(Int, split(line, ' '))
    if length(currentPath) == numCities
        currentPath .= currentPath .+ 1
    else
        currentPath = collect(1:numCities)
    end
    resultCost = calculateCost(currentPath, graphMatrix)
    resultPath = currentPath

    # Główna pętla algorytmu
    endTime = time()
    startTime = time()
    for iteration in 1:maxIterations
        similarPaths = generateSimilarPaths(currentPath)
        bestCostSimilarPaths = Inf
        bestSimilarPath = Vector{Int}()

        # Szukanie najlepszego sąsiada
        for path in similarPaths
            if !(path in tabuList)
                tmpCost = calculateCost(path, graphMatrix)
                if tmpCost < bestCostSimilarPaths
                    bestCostSimilarPaths = tmpCost
                    bestSimilarPath = path
                end
            end
        end

        if isempty(bestSimilarPath)
            break
        end

        currentPath = bestSimilarPath
        push!(tabuList, bestSimilarPath)

        if length(tabuList) > maxTabuListSize
            popfirst!(tabuList)
        end

        if resultCost > bestCostSimilarPaths
            resultPath = currentPath
            resultCost = bestCostSimilarPaths
            endTime = time()
        end
    end

    # Zwrócenie rezultatów
    result = AlgorithmResult(round(Int, (endTime - startTime) * 1000000), resultCost, resultPath)
    return result
end

function main()
    filename = ARGS[1]

    # Sprawdzenie istnienia i wczytanie odpowiednich plików
    if !isdir("testInstance/")
        mkdir("testInstance/")
    end
    
    if !isfile("testInstance/" * filename)
        println("File not found")
        return
    else
        data = readdlm("testInstance/" * filename)
        try
            global graphMatrix = Matrix{Float64}(data)
        catch
            return
        end
    end

    # Uruchomienie algorytmu
    result = tabuSearch(graphMatrix)

    # Sprawdzenie czy folder istnieje
    if !isdir("juliaResult/")
        mkdir("juliaResult/")
    end

    # Zapisanie rezultatów do plików CSV
    resultName = basename(filename)
    open("juliaResult/result.csv", "a") do f
        println(f, "$resultName;$(result.time);$(result.cost)")
    end

    open("juliaResult/$resultName.csv", "a") do f
        println(f, "$(result.time);$(result.cost)")
    end

    # Wyświetlenie rezultatów
    push!(result.path, result.path[1])
    println("cost: $(result.cost), time: $(result.time), path: $(result.path)")
end

# Początek wykonywania programu
main()
