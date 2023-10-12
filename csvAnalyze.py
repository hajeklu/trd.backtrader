import csv

# Open the CSV file
with open('NZD.csv', 'r') as file:
    # Create a CSV reader
    csv_reader = csv.reader(file)

    hashMap = {}
    # Iterate over rows in the CSV file
    for row in csv_reader:
        [key, value] = row
        if value < '0':
            continue

        if key in hashMap:
            hashMap[key] = hashMap[key] + 1
        else:
            hashMap[key] = 1

    sorted_dict = dict(sorted(hashMap.items(), key=lambda item: item[1]))

    print(sorted_dict)
