# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask,render_template,request,redirect
import pickle

#Data Structure and functions
class Node:
    def __init__(self, item=None, right=None, left=None):
        self.item = item
        self.right = right
        self.left = left

def create_tree(lst):
    if not lst:
        return None

    mid = len(lst) // 2
    root = Node(lst[mid])
    root.left = create_tree(lst[:mid])
    root.right = create_tree(lst[mid + 1:])
    return root

#[2, 'b', [['14a', '3', 'Occupied', 'ownership status', 'ramesh', ['8939155122', Tenant name, tenant no], ['Unpaid', 20000]]]]

def load_tree():
    try:
        with open("tree.pkl", "rb") as file:
            root = pickle.load(file)
            print("Tree loaded successfully!")
            return root
    except Exception as e:
        print("Error occurred while loading the data:", e)
        return None

def save_tree(root):
    try:
        with open("tree.pkl", "wb") as file:
            pickle.dump(root, file)
            print("Data saved successfully!")
    except Exception as e:
        print("Error occurred while saving the data:", e)

def change_lock(password):
    try:
        with open("password.pkl", "wb") as file:
            pickle.dump(password, file)
    except Exception as e:
        return("Error occurred while changing password:",e)
    
def load_password():
    try:
        with open("password.pkl", "rb") as file:
            password = pickle.load(file)
            return password
    except Exception as e:
        print("Error occurred while loading the data:", e)
        return None
    
def generate_all_block_names(root):
    block_names = []
    def traverse(node):
        if node:
            traverse(node.left)
            block_names.append(node.item[1])
            traverse(node.right)
    traverse(root)
    return block_names

def search_block(root,searched_block_name):
    def traverse(node):
        if node:
            if node.item[1] == searched_block_name:
                print("Node item is present:", node.item)
                return True
            if traverse(node.left):
                return True
            if traverse(node.right):
                return True
        return False
    return traverse(root)

def generate_all_block_details(root):
    block_details = []
    def traverse(node):
        if node:
            traverse(node.left)
            block_details.append(node.item)
            traverse(node.right)
    traverse(root)
    return block_details

def generate_all_house_details(root, block_to_be_generated=None):
    if block_to_be_generated is None:
        return None
    block_details = generate_all_block_details(root)
    house_details = []
    block_found = False
    for block in block_details:
        if block[1] == block_to_be_generated:
            for house in block[2]:
                house_details.append(house)
            block_found = True
            break
    if not block_found:
        print("Block not found.")
    return house_details

def find_house(root, block, house):
    def traverse(node):
        if node:
            if node.item[1] == block:
                for i in node.item[2]:
                    if i[0] == house:
                        return i
            result = traverse(node.left)
            if result is not None:
                return result
            return traverse(node.right)
    return traverse(root)

def generate_house_numbers(root,block_name):
    block_details=generate_all_block_details(root)
    for block in block_details:
        if block[1]==block_name:
            return [house[0] for house in block[2]]
        
def maintenance_update(root,block_name,house_number,maintenance_status,dueamt):
    block_details = generate_all_block_details(root)
    for block in block_details:
        if block[1] == block_name:
            for house in block[2]:
                if house[0] == house_number:
                    if maintenance_status == "Paid":
                        house[6][0] = "Paid"
                        house[6][1] = 0
                    elif maintenance_status == "Unpaid":
                        house[6][0] = "Unpaid"
                        house[6][1] += int(dueamt)
                    else:
                        raise ValueError("Enter a valid option!")
                    rootnode=create_tree(block_details)
                    save_tree(rootnode)
                    return root
                
def reset_maintenance(root,bhk2amt,bhk3amt,penalty):
    block_details=generate_all_block_details(root)
    for block in block_details:
        for house in block[2]:
            if house[2]=="Occupied":
                    pending=house[6][1]
                    pending=int(pending)
                    if house[6][0]=="Unpaid":
                       pending += int(penalty)
                    house[6][0] = "Unpaid"
                    if house[1]=="2":
                        pending += int(bhk2amt)
                    elif house[1]=="3":
                        pending += int(bhk3amt)
                    house[6][1]=pending
    rootnode=create_tree(block_details)
    save_tree(rootnode)

def search_unoccupied_houses(root,bhk):
    unoccupied_houses = []
    def traverse(node):
        if node:
            traverse(node.left)
            for house in node.item[2]:
                if house[1] == bhk and  house[2].lower() == "unoccupied":
                    unoccupied_houses.append((node.item[1], house[0]))
            traverse(node.right)
    traverse(root)
    return unoccupied_houses

#Integration

app = Flask(__name__)

@app.route('/home_page')
def home():
    return render_template('home page.html')
@app.route('/residents')
def residents():
    return render_template('house_info.html')
@app.route('/flats')
def flats():
    return render_template('resident info pg.html')
@app.route('/payments')
def payments():
    return render_template('payment.html')
@app.route('/complaint')
def complaint():
    return render_template('complaint.html')
@app.route('/announcements')
def announcements():
    return render_template('announcements.html')


@app.route('/searchinfo', methods=['GET', 'POST'])
def searchinfo():
    if request.method == 'POST':
        r=load_tree()
        block_name = request.form.get('blockname')
        block_present = search_block(r,block_name)
        return render_template('search-block.html', blockpresent=block_present)
    else:
        return render_template('search-block.html')
    
@app.route('/blockname') # Show all block names
def blockname():
    r = load_tree()
    block_names = generate_all_block_names(r) 
    return render_template('block_names.html', block_names=block_names)

@app.route('/house_info', methods=['GET', 'POST'])
def house_info():
    r = load_tree()
    if request.method == 'POST':
        block_to_be_generated = request.form.get('block-name')
        house_details = generate_all_house_details(r, block_to_be_generated)
        return render_template('house_info.html', block_name=block_to_be_generated, house_details=house_details)
    else:
        return render_template('house_info.html')

@app.route('/edit_details', methods=['GET', 'POST'])
def edit_details():
    r = load_tree()
    if request.method == 'POST':
        block = request.form.get('block')
        house_number = request.form.get('house_number')
        new_occupancy_status = request.form.get('occupancy_status')
        new_owner_name = request.form.get('owner_name')
        new_ownership_status = request.form.get('ownership_status')
        owner_tele = request.form.get('owner_tele')
        tenant_name = request.form.get('tenant_name')
        tenant_tele = request.form.get('tenant_tele')
        maintenance_status = request.form.get('maintenance_status')
        due_amount = request.form.get('due_amount')

        # Check if any of the required fields are empty
        if not block or not house_number or not new_occupancy_status or not new_owner_name or not new_ownership_status or not owner_tele or not tenant_name or not tenant_tele or not maintenance_status or not due_amount:
            return render_template('not_enough_info.html')

        # Find the house in the binary tree
        house = find_house(r, block, house_number)
        if house:
            # Update the house details
            house[2] = new_occupancy_status
            house[4] = new_owner_name
            house[3] = new_ownership_status
            house[5][0] = owner_tele
            house[5][1] = tenant_name
            house[5][2] = tenant_tele
            house[6][0] = maintenance_status
            house[6][1] = due_amount

            save_tree(r)  # Save the updated tree
            return render_template('edit-success.html')
        else:
            return render_template('edit-error.html')
    return render_template('edit-details.html')


@app.route('/delete_house', methods=['GET', 'POST'])
def delete_house():
    r = load_tree()
    if request.method == 'POST':
        block_name = request.form['block_name']
        house_number = request.form['house_number']

        block_details = generate_all_block_details(r)
        block_index = -1
        for block in block_details:
            block_index += 1
            if block[1] == block_name:
                houses = generate_house_numbers(r, block_name)
                house_index = -1
                for house in houses:
                    house_index += 1
                    if house == house_number:
                        block_details[block_index][2].pop(house_index)
                        save_tree(r)
                        return render_template('deletion_success.html')

        return render_template('house_not_found_error.html')
    
    return render_template('delete_house.html')


@app.route('/add_house', methods=['GET', 'POST'])
def add_house():
    r=load_tree()
    if request.method == 'POST':
        block_name = request.form['block_name']
        house_number = request.form['house_number']
        bhk = request.form['bhk']
        occupancy_status = int(request.form['occupancy_status'])
        if occupancy_status == 1:
            occupancy_status = "Occupied"
            owner_name = request.form['owner_name']
            ownership_status = request.form['ownership_status']
        elif occupancy_status == 0:
            occupancy_status = "Unoccupied"
            owner_name = None
            ownership_status = None
        else:
            return "Enter a valid option"

        owner_telephone = None
        tenant_name = None
        tenant_tele = None
        if occupancy_status == "Occupied":
            owner_telephone = request.form['owner_telephone']
            if ownership_status.lower() == "rental":
                tenant_name = request.form['tenant_name']
                tenant_tele = request.form['tenant_telephone']

        owner_details = [owner_telephone, tenant_name, tenant_tele]
        maintenance = ["Unpaid", 0]

        block_details = generate_all_block_details(r)
        for block in block_details:
            if block[1] == block_name:
                houses=generate_house_numbers(r,block_name)
                if house_number not in houses:
                    block[2].append([house_number, bhk, occupancy_status, ownership_status, owner_name, owner_details, maintenance])
                    save_tree(r)
                    return render_template('add_house_success.html')
                else:
                    return render_template('add_house_error.html', error="House already exists!")
        return render_template('add_house_error.html', error="Block not found!")

    return render_template('add-hdetails.html')

@app.route('/update',methods=['GET','POST'])
def update():
    r=load_tree()
    if request.method=="POST":
        blockno=request.form.get('block-name')
        houseno=request.form.get('house-number')
        dueamt=request.form.get('due-amount')
        status=request.form.get('maintenance-status')
        if status.lower()=='paid':
            dueamt=0
        maintenance_update(r,blockno,houseno,status.capitalize(),int(dueamt))
        return render_template('update-maintenance.html')
    return render_template('update-maintenance.html')


@app.route('/add_block', methods=['GET', 'POST'])
def add_block():
    r = load_tree()
    if request.method == 'POST':
        block_name = request.form['block_name']
        block_details = generate_all_block_details(r)
        for block in block_details:
            if block[1] == block_name:
                return render_template('add_block_error.html', error="Block already exists!")
        block_number=len(block_details) + 1
        new_block = [block_number, block_name, []]
        block_details.append(new_block)
        if r is None:
            r = Node(new_block)
        else:
            current = r
            while True: 
                if block_number < current.item[0]:
                    if current.left is None:
                        current.left = Node(new_block)
                        break
                    else:
                        current = current.left
                else:
                    if current.right is None:
                        current.right = Node(new_block)
                        break
                    else:
                        current = current.right
        save_tree(r)
        return render_template('add_block_success.html', block_name=block_name)

    return render_template('add_block.html')

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        r = load_tree()
        bhk2amt = request.form['bhk_2']
        bhk3amt = request.form['bhk_3']
        penalty = request.form['penalty']
        reset_maintenance(r, bhk2amt, bhk3amt, penalty)
        return render_template('reset_successful.html')
    else:
        return render_template('reset-maintenance.html')


@app.route('/search_unoccupied_houses', methods=['GET', 'POST'])
def unoccupied_houses():
    if request.method == 'POST':
        r = load_tree()
        bhk = request.form['bhk']
        houses = search_unoccupied_houses(r, bhk)
        return render_template('unoccupied_house.html', unoccupied_houses=houses)
    
    return render_template('search_house.html')

@app.route('/', methods=['POST', 'GET'])
def lock():
    if request.method == 'POST':
        entered_password = request.form['password']
        password = load_password()
        if password == entered_password:
            return redirect('/home_page')
        else:
            error = "Wrong password. Please try again!"
            return render_template('lock_page.html', error=error)
    return render_template('lock_page.html')

# main driver function
if __name__ == '__main__':
    app.run(debug=True)