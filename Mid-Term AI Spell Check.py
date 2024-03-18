#C:\Users\reese\OneDrive\Desktop\TXST\Applied AI - Spring 2024\Mid Term\test_source.txt

#libaries 
import nltk
from nltk.corpus import brown
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag
from nltk.probability import FreqDist
import zipfile
import csv

##checks if you downloaded the necessary NLTK data 
##nltk.download('brown')
##nltk.download('punkt')
##nltk.download('averaged_perceptron_tagger')

#loads brown and creates a freq distribution of words
brown_words = set(word.lower() for word in brown.words() if word.isalpha())
fdist = FreqDist(word.lower() for word in brown.words() if word.isalpha())

#loads additional words from zip file
def load_words_from_zip(zip_file_path):
    words_dict = {}
    with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
        for file_name in zip_file.namelist():
            with zip_file.open(file_name) as file:
                words = set(file.read().decode('utf-8').lower().split())
            words_dict[file_name] = words
    return words_dict

#path to zip file 
additional_words_zip = 'C:/Users/reese/OneDrive/Desktop/TXST/Applied AI - Spring 2024/Mid Term/Words for Spell Checker.zip' #new users would need to update this with their path 
additional_words_dict = load_words_from_zip(additional_words_zip)

#combines the additional words with Brown words
complete_word_list = brown_words.union(*additional_words_dict.values())

#levenshtein distance: counts how many changes that need to be made to turn one word into the other
def levenshtein_distance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    distances = range(len(s1) + 1)
    for index2, char2 in enumerate(s2):
        new_distances = [index2 + 1]
        for index1, char1 in enumerate(s1):
            if char1 == char2:
                new_distances.append(distances[index1])
            else:
                new_distances.append(1 + min((distances[index1], distances[index1 + 1], new_distances[-1])))
        distances = new_distances
    return distances[-1]

#suggests correction for misspelled word 
def suggest_word(misspelled_word, word_list, max_distance=2, num_suggestions=3):
    suggestions = []
    for word in word_list:
        distance = levenshtein_distance(misspelled_word, word)
        if distance <= max_distance:
            suggestions.append((word, distance))
    suggestions.sort(key=lambda x: (-fdist.get(x[0], 0), x[1])) 
    return [word for word, distance in suggestions[:num_suggestions]]

#check spelling in list of sentences
def check_spelling_in_sentences(sentences, word_list):
    corrections = {}
    for sentence in sentences:
        tagged_words = pos_tag(word_tokenize(sentence))
        for word, tag in tagged_words:
            if word.isalpha() and tag not in ['NNP', 'NNPS']:
                lower_word = word.lower()
                if lower_word not in word_list:
                    suggestions = suggest_word(lower_word, word_list)
                    if suggestions:
                        corrections[word] = suggestions
    return corrections

#saves corrections to csv file 
def save_corrections_to_csv(corrections, file_name):
    with open(file_name + '.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Misspelled Word", "Suggestions"])
        for incorrect_word, suggestions in corrections.items():
            writer.writerow([incorrect_word, ', '.join(suggestions)])
    print(f"\nSpell checking results have been saved in the CSV file: {file_name}.csv")


#look through test file, find misspelled words, and suggests corrections with error messages
def process_text_interactively(file_path, word_list, csv_file_name):
    try:
        with open(file_path, 'r') as file:
            text_content = file.read()
    except FileNotFoundError:
        print(f"Error! The file at {file_path} was not found. Please check the path and try again.") #error handling 
        return

    sentences = sent_tokenize(text_content)
    corrections = {}

    for i in range(0, len(sentences), 3):
        current_sentences = sentences[i:i+3]
        temp_corrections = check_spelling_in_sentences(current_sentences, word_list)
        corrections.update(temp_corrections)
        print(f"\nChecking sentences {i+1} to {i+len(current_sentences)}:")
        if temp_corrections:
            print("\nSpelling corrections needed:")
            for incorrect_word, suggestions in temp_corrections.items():
                print(f"{incorrect_word}: {suggestions}")
        else:
            print("No spelling corrections needed.")
        
        if i + 3 < len(sentences):
            while True:
                continue_checking = input("\nDo you want to continue checking the next three sentences? (yes/no): ")
                if continue_checking.lower() in ['yes', 'no']:
                    break
                else:
                    print("Invalid input. Please answer 'yes' or 'no'.") #error handling
            if continue_checking.lower() != 'yes':
                break
    else:
        print("Spell checking of the document is complete.")

    while True:
        choice = input("\nDo you want to upload the corrections to a CSV file? (yes/no): ").lower()
        if choice == 'yes':
            while True:
                try:
                    save_corrections_to_csv(corrections, csv_file_name)
                    break 
                except Exception as e:
                    print(f"An error has occurred while saving the file: {e}. Please try again.") #error handling
                    csv_file_name = input("Enter a new file name to save the CSV spreadsheet: ")
            break  
        elif choice == 'no':
            print("Suggestions have not been saved.")
            break
        else:
            print("Invalid choice. Please answer 'yes' or 'no'.") #error handling

#main menu to provide user with options 
def main_menu():
    while True:
        print("\nSpell Checker Menu:")
        print("1. Check spellings three sentences at a time")
        print("2. Upload the entire document to a CSV file")
        print("3. Exit")
        choice = input("Enter your choice (1/2/3): ")

        if choice == '1':
            while True:
                file_path_correct = False
                while not file_path_correct:
                    file_path = input("\nEnter the path to the text file: ")
                    try:
                        with open(file_path, 'r') as file:
                            file_path_correct = True
                    except FileNotFoundError:
                        print(f"Error! The file at {file_path} was not found. Please check the path and try again.")
                        
                csv_file_name = input("\nEnter the file name to save the CSV spreadsheet: ") #enter random name like apple or dog 
                try:
                    process_text_interactively(file_path, complete_word_list, csv_file_name)
                    break  
                except Exception as e:
                    print(f"An unexpected error occurred: {e}. Please try again.") #error handling
        elif choice == '2':
            while True:
                file_path = input("\nEnter the path to the text file: ")
                try:
                    with open(file_path, 'r') as file:
                        text_content = file.read()
                    corrections = check_spelling_in_sentences(sent_tokenize(text_content), complete_word_list)
                    file_name = input("\nEnter the file name to save the CSV spreadsheet: ")
                    save_corrections_to_csv(corrections, file_name)
                    break  
                except FileNotFoundError:
                    print(f"Error! The file at {file_path} was not found. Please check the path and try again.") #error handling
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.") #error handling


main_menu()
