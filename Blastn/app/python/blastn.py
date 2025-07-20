# blastn nucleotide
with open("database.txt", "r") as file:
    database = [line.strip() for line in file if line.strip()]
query_sequence = "AGCTGAC"
words = []
results = []
filtered_results = []
best_results = []
hsp_list = []
kmer = 3
print(len(database))

def preprocess_query():
    for i in range(len(query_sequence) - (kmer - 1)):
        words.append(query_sequence[i:i + kmer])
    print(words)


def seed_searching():
    for subject_index,subject in enumerate(database):
        for word_index,word in enumerate(words):
            hsp_list_temp = []
            # word_score_max = 0
            for i in range(len(subject)-(kmer - 1)):
                match = True
                for k in range(kmer):
                    if subject[i+k] != word[k]:
                        match = False
                        break
                if match:
                    hsp_list_temp.append([kmer,subject_index,word_index,i])
            hsp_list.extend(hsp_list_temp)
    print(hsp_list)



def extend_alignment():
    gap_thre = 3
    for i in range (len(hsp_list)):

        word_index = hsp_list[i][2]
        word = words[word_index]
        subject_index = hsp_list[i][1]
        subject = database[subject_index]
        subject_pos = hsp_list[i][3]

        alignment_score = kmer
        alignment_thre = -50
        q_left = word_index -1
        s_left = subject_pos -1
        while q_left >= 0 and s_left >= 0 and alignment_score > alignment_thre:
            if (query_sequence[q_left] == subject[s_left]):
                alignment_score += 1

            else:
                alignment_score += -3
            q_left -= 1
            s_left -= 1

        q_right = word_index + kmer
        s_right = subject_pos + kmer
        while q_right < len(query_sequence) and s_right < len(subject) and alignment_score > alignment_thre:
            if (query_sequence[q_right] == subject[s_right]):
                alignment_score += 1

            else:
                alignment_score += -3
            q_right += 1
            s_right += 1

        aligned_query = query_sequence[q_left + 1:q_right]
        aligned_subject = subject[s_left + 1:s_right]

        if alignment_score > gap_thre:
            pass
            # dp_table =


        # results.append([alignment_score,aligned_query,aligned_subject,subject_index,word_index,subject_pos])
        identity = calculate_identity(aligned_query, aligned_subject)
        results.append([alignment_score, aligned_query, aligned_subject, subject_index, word_index, subject_pos, identity])

    print(results)
    if len(results) == 0:
        print("none")

def filter():
    max_score = -10
    thre = -10
    for i in range(len(results)):


        if results[i][0] > thre:
            filtered_results.append(results[i])
        if results[i][0] > max_score:
            best_results.clear()
            best_results.append(results[i])
            max_score = results[i][0]
        elif results[i][0] == max_score:
            best_results.append(results[i])

    print("best",best_results)
    print("filtered",filtered_results)

def calculate_identity(aligned_query, aligned_subject):
    match_count = 0
    for a, b in zip(aligned_query, aligned_subject):
        if a == b:
            match_count += 1
    return (match_count / len(aligned_query)) * 100

def print_result():
    for res in filtered_results:
        score, q_align, s_align, subj_idx, q_idx, s_pos, identity = res
        print(f"Score: {score}, Identity: {identity:.2f}%")
        print(f"Aligned Query   : {q_align}")
        print(f"Aligned Subject : {s_align}")
        print(f"Subject Sequence #: {subj_idx}, Query Position: {q_idx}, Subject Position: {s_pos}")
        print("-" * 50)


preprocess_query()
seed_searching()
extend_alignment()
filter()
print_result()
