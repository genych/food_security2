__author__ = "Kris"

from flask import Flask, render_template
from food_security.forms import Select_Field_Form, place_name_maker
from food_security.Miner import Data_Miner

app = Flask(__name__)
app.secret_key = "1234"
#CSV_PUT.csv_put_geocords(var="poop")

@app.route('/', methods=['POST', 'GET'])
def selection():
    form = Select_Field_Form()
    # setting form to class select_field_form
    partial_link_from_selectfield = form.selectfield.data
    # this is the users selection from the selectfield but it is the link, not the place name
    burrough_choice = place_name_maker(partial_link_from_selectfield)
    # sennds

    if partial_link_from_selectfield is not "None":
        print("You have selected, ", burrough_choice, "taking you to that page")
        Data_Miner.get_all_links(partial_link_from_selectfield)

        return render_template('results.html',
                               form=form,
                               burrough_choice=burrough_choice.title(),
                               link = Data_Miner.make_full_link(partial_link_from_selectfield),
                               my_string="You have Selected")
    return render_template('selectfield.html', form=form)




@app.route('/results', methods=['POST', 'GET'])
def result_method():
    return render_template('results.html')

"""

if __name__ == '__main__':
    app.run(debug=True)
"""