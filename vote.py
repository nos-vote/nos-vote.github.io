from boa.interop.Neo.Storage import GetContext, Put, Delete, Get
from boa.interop.Neo.Runtime import CheckWitness, Serialize, Deserialize, Notify

get_all_ids = "GET_ALL_QUESTIONS"

# Need an object on blockchain to keep track of all existing IDs
# Check if it exists, if not, create a blank one and put on blockchain
def check_allQuestionIds():
    all_questions = Get(GetContext(), get_all_ids)
    if not all_questions:
        Notify("[!] Creating all_question_ids object")
        all_question_ids = {}
        serialized = Serialize(all_question_ids)
        Put(GetContext(), get_all_ids, serialized)

def addQuestionId(questionId, question):
    Notify("[!] Add QuestionID to all_question_ids object")
    serial = Get(GetContext(), get_all_ids)
    all_question_ids = Deserialize(serial)
    all_question_ids[questionId] = question
    new_serial = Serialize(all_question_ids)
    Put(GetContext(), get_all_ids, new_serial)
    Notify("[!] Added QuestionID to all_question_ids object")

def removeQuestionId(questionId):
    Notify("[!] Remove QuestionID to all_question_ids object")
    serial = Get(GetContext(), get_all_ids)
    all_question_ids = Deserialize(serial)
    all_question_ids.remove(questionId)
    new_serial = Serialize(all_question_ids)
    Put(GetContext(), get_all_ids, new_serial)
    Notify("[!] Removed QuestionID from all_question_ids object")
    
        
# Main Operation
#
def Main(operation, args):
    """
    Main definition for the smart contracts

    :param operation: the operation to be performed
    :type operation: str

    :param args: list of arguments.
        args[0] is always sender script hash
        args[1] is always question_id
        args[2] is a question itself (optional, only used when registering new questions)

    :return:
        byterarray: The result of the operation
    """

    # Am I who I say I am?
    user_hash = args[0]
    authorized = CheckWitness(user_hash)
    if not authorized:
        Notify("[!] Not Authorized")
        return False
    Notify("[+] Authorized")

    if operation == "RegisterQuestion":
        if len(args) != 3:
            Notify("[!] Not enough arguments! Expecting: [0] user_hash [1] question_id [2] question")
            return False
        question_id = args[1]
        question = args[2]

    elif operation == "GetAllQuestions":
        if len(args) != 1:
            Notify("[!] Too many arguments! Expecting: [0] user_hash")
            return False

    else:
        if len(args) != 2:
            Notify("[!] Not enough arguments! Expecting: [0] user_hash [1] question_id")
            return False
        question_id = args[1]

    check_allQuestionIds()

    # Act based on requested operation
    if operation == "RegisterQuestion":
        Notify("[*] RegisterQuestion")
        question_exists = Get(GetContext(), question_id)
        if question_exists:
            Notify("[!] Question already exists")
            return False
        else:
            voters = {}
            #voters[user_hash] = "voted"
            question_object = {
                "question_id": question_id,
                "owner": user_hash,
                "question": question,
                "voters": voters,
                "yes_counter": 0,
                "no_counter": 0 }
            temp_question_object = Serialize(question_object)
            Put(GetContext(), question_id, temp_question_object)
            addQuestionId(question_id, question)
            Notify("[+] Question Registered")
            return True

    elif operation == "VoteYes":
        Notify("[*] VoteYes")
        temp_question_object = Get(GetContext(), question_id)
        if temp_question_object:
            question_object = Deserialize(temp_question_object)
            voters = question_object["voters"]
            if has_key(voters, user_hash):
                Notify("[!] Already voted")
                return False
            else:
                counter = question_object["yes_counter"]
                counter = counter + 1
                question_object["yes_counter"] = counter
                voters[user_hash] = "voted"
                question_object["voters"] = voters
                temp_question_object = Serialize(question_object)
                Put(GetContext(), question_id, temp_question_object)
                Notify("[+] Vote registered")
                return True
        else:
            Notify("[!] Question ID not found!")
            return False

    elif operation == "VoteNo":
        Notify("[*] VoteNo")
        temp_question_object = Get(GetContext(), question_id)
        if temp_question_object:
            question_object = Deserialize(temp_question_object)
            voters = question_object["voters"]
            if has_key(voters, user_hash):
               Notify("[!] Already voted")
               return False
            else:
                Notify("COUNTER")
                Notify(counter)
                counter = question_object["no_counter"]
                counter = counter + 1
                question_object["no_counter"] = counter
                voters[user_hash] = "voted"
                question_object["voters"] = voters
                temp_question_object = Serialize(question_object)
                Put(GetContext(), question_id, temp_question_object)
                Notify("[+] Vote registered")
                return True
        else:
            Notify("[!] Question ID not found!")
            return False

    elif operation == "RemoveQuestion":
        Notify("[*] RemoveQuestion")
        temp_question_object = Get(GetContext(), question_id)
        if temp_question_object:
            question_object = Deserialize(temp_question_object)
            if question_object["owner"] is user_hash:
                # Delete the question
                Delete(GetContext(), question_id)
                Notify("[+] Question removed")
                removeQuestionId(question_id)
                return True
            else:
                Notify("[!] You are not the owner of the question.")
                return False
        else:
            Notify("[!] Question ID not found!")
            return False

    elif operation == "GetQuestion":
        Notify("[*] GetQuestion")
        temp_question_object = Get(GetContext(), question_id)
        if temp_question_object:
            question_object = Deserialize(temp_question_object)
            return question_object
        else:
            Notify("[!] Question ID not found!")
            return False

    elif operation == "GetYesCounter":
        Notify("[*] GetYesCounter")
        temp_question_object = Get(GetContext(), question_id)
        if temp_question_object:
            question_object = Deserialize(temp_question_object)
            return question_object["yes_counter"]
        else:
            Notify("[!] Question ID not found!")
            return False

    elif operation == "GetNoCounter":
        Notify("[*] GetNoCounter")
        temp_question_object = Get(GetContext(), question_id)
        if temp_question_object:
            question_object = Deserialize(temp_question_object)
            return question_object["no_counter"]
        else:
            Notify("[!] Question ID not found!")
            return False

    elif operation == "GetAllQuestions":
        Notify("[*] GetAllQuestions")
        serial = Get(GetContext(), get_all_ids)
        if serial:
            # Bug in NEO-LOCAL? Crashed parsing ToJson...
            # May need to implement it to return strings instead
            # of the object...
            Notify("[*] Serial exists")
            all_questions = Deserialize(serial)
            return all_questions
        else:
            Notify("[!] All Questions object not found!")
            return False

    else:
        Notify("[!] Operation not found!")

    return False

