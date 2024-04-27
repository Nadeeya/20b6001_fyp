// dynamic field creation with javascript

// import country from 'country-list-js';

//academic Record
const addBtn =document.querySelector(".add_academic_record");
const input = document.querySelector(".inp_academic_record");

//membership fellowship
const addBtn_membership_fellowhsip = document.querySelector(".add_membership_fellowship");
const input_membership_fellowship = document.querySelector(".inp_membership_fellowship");

//employment Record
//erhe = employment record higher education
const addBtn_erhe = document.querySelector(".add_erhe");
const input_erhe = document.querySelector(".inp_erhe");

const addBtn_eri = document.querySelector(".add_eri");
const input_eri = document.querySelector(".inp_eri");

//teaching and supervision

const addBtn_courses = document.querySelector(".add_courses");
const input_courses = document.querySelector(".inp_courses");

//language

const addBtn_language  = document.querySelector(".add_language");
const input_language = document.querySelector(".inp_language");

//children

const addBtn_children = document.querySelector(".add_children");
const input_children = document.querySelector(".input_children")

//list of country
 const countryList = ["Afghanistan","Albania","Algeria","American Samoa","Andorra",   "Angola",
   "Anguilla",
   "Antarctica",
   "Antigua and Barbuda",
   "Argentina",
   "Armenia",
   "Aruba",
   "Australia",
   "Austria",
   "Azerbaijan",
   "Bahamas (the)",
   "Bahrain",
   "Bangladesh",
   "Barbados",
   "Belarus",
   "Belgium",
   "Belize",
   "Benin",
   "Bermuda",
   "Bhutan",
   "Bolivia (Plurinational State of)",
   "Bonaire, Sint Eustatius and Saba",
   "Bosnia and Herzegovina",
   "Botswana",
   "Bouvet Island",
   "Brazil",
   "British Indian Ocean Territory (the)",
   "Brunei Darussalam",
   "Bulgaria",
   "Burkina Faso",
   "Burundi",
   "Cabo Verde",
   "Cambodia",
   "Cameroon",
   "Canada",
   "Cayman Islands (the)",
   "Central African Republic (the)",
   "Chad",
   "Chile",
   "China",
   "Christmas Island",
   "Cocos (Keeling) Islands (the)",
   "Colombia",
   "Comoros (the)",
   "Congo (the Democratic Republic of the)",
   "Congo (the)",
   "Cook Islands (the)",
   "Costa Rica",
   "Croatia",
   "Cuba",
   "Curaçao",
   "Cyprus",
   "Czechia",
   "Côte d'Ivoire",
   "Denmark",
   "Djibouti",
   "Dominica",
   "Dominican Republic (the)",
   "Ecuador",
   "Egypt",
   "El Salvador",
   "Equatorial Guinea",
   "Eritrea",
   "Estonia",
   "Eswatini",
   "Ethiopia",
   "Falkland Islands (the) [Malvinas]",
   "Faroe Islands (the)",
   "Fiji",
   "Finland",
   "France",
   "French Guiana",
   "French Polynesia",
   "French Southern Territories (the)",
   "Gabon",
   "Gambia (the)",
   "Georgia",
   "Germany",
   "Ghana",
   "Gibraltar",
   "Greece",
   "Greenland",
   "Grenada",
   "Guadeloupe",
   "Guam",
   "Guatemala",
   "Guernsey",
   "Guinea",
   "Guinea-Bissau",
   "Guyana",
   "Haiti",
   "Heard Island and McDonald Islands",
   "Holy See (the)",
   "Honduras",
   "Hong Kong",
   "Hungary",
   "Iceland",
   "India",
   "Indonesia",
   "Iran (Islamic Republic of)",
   "Iraq",
   "Ireland",
   "Isle of Man",
   "Israel",
   "Italy",
   "Jamaica",
   "Japan",
   "Jersey",
   "Jordan",
   "Kazakhstan",
   "Kenya",
   "Kiribati",
   "Korea (the Democratic People's Republic of)",
   "Korea (the Republic of)",
   "Kuwait",
   "Kyrgyzstan",
   "Lao People's Democratic Republic (the)",
   "Latvia",
   "Lebanon",
   "Lesotho",
   "Liberia",
   "Libya",
   "Liechtenstein",
   "Lithuania",
   "Luxembourg",
   "Macao",
   "Madagascar",
   "Malawi",
   "Malaysia",
   "Maldives",
   "Mali",
   "Malta",
   "Marshall Islands (the)",
   "Martinique",
   "Mauritania",
   "Mauritius",
   "Mayotte",
   "Mexico",
   "Micronesia (Federated States of)",
   "Moldova (the Republic of)",
   "Monaco",
   "Mongolia",
   "Montenegro",
   "Montserrat",
   "Morocco",
   "Mozambique",
   "Myanmar",
   "Namibia",
   "Nauru",
   "Nepal",
   "Netherlands (the)",
   "New Caledonia",
   "New Zealand",
   "Nicaragua",
   "Niger (the)",
   "Nigeria",
   "Niue",
   "Norfolk Island",
   "Northern Mariana Islands (the)",
   "Norway",
   "Oman",
   "Pakistan",
   "Palau",
   "Palestine, State of",
   "Panama",
   "Papua New Guinea",
   "Paraguay",
   "Peru",
   "Philippines (the)",
   "Pitcairn",
   "Poland",
   "Portugal",
   "Puerto Rico",
   "Qatar",
   "Republic of North Macedonia",
   "Romania",
   "Russian Federation (the)",
   "Rwanda",
   "Réunion",
   "Saint Barthélemy",
   "Saint Helena, Ascension and Tristan da Cunha",
   "Saint Kitts and Nevis",
   "Saint Lucia",
   "Saint Martin (French part)",
   "Saint Pierre and Miquelon",
   "Saint Vincent and the Grenadines",
   "Samoa",
   "San Marino",
   "Sao Tome and Principe",
   "Saudi Arabia",
   "Senegal",
   "Serbia",
   "Seychelles",
   "Sierra Leone",
   "Singapore",
   "Sint Maarten (Dutch part)",
   "Slovakia",
   "Slovenia",
   "Solomon Islands",
   "Somalia",
   "South Africa",
   "South Georgia and the South Sandwich Islands",
   "South Sudan",
   "Spain",
   "Sri Lanka",
   "Sudan (the)",
   "Suriname",
   "Svalbard and Jan Mayen",
   "Sweden",
   "Switzerland",
   "Syrian Arab Republic",
   "Taiwan",
   "Tajikistan",
   "Tanzania, United Republic of",
   "Thailand",
   "Timor-Leste",
   "Togo",
   "Tokelau",
   "Tonga",
   "Trinidad and Tobago",
   "Tunisia",
   "Turkey",
   "Turkmenistan",
   "Turks and Caicos Islands (the)",
   "Tuvalu",
   "Uganda",
   "Ukraine",
   "United Arab Emirates (the)",
   "United Kingdom of Great Britain and Northern Ireland (the)",
   "United States Minor Outlying Islands (the)",
   "United States of America (the)",
   "Uruguay",
   "Uzbekistan",
   "Vanuatu",
   "Venezuela (Bolivarian Republic of)",
   "Viet Nam",
   "Virgin Islands (British)",
   "Virgin Islands (U.S.)",
   "Wallis and Futuna",
   "Western Sahara",
   "Yemen",
   "Zambia",
   "Zimbabwe",
   "Åland Islands",
 ];

function removeInput(){
    this.parentElement.remove();
}

//academic records

function addInput(){
    // academic name or name of degree
    const academic_name = document.createElement("input");
    academic_name.type = "text"; 
    academic_name.placeholder = "Name of degree. Eg: Doctor of Philosophy (Finance)";
    // academic_name.className = "academic_name";
    academic_name.style = "width:35%";
    academic_name.name = "academic_name";

    // Institute
    const institute = document.createElement("input");
    institute.type = "text";
    institute.placeholder = "Institution attended. Eg: Universiti Brunei Darussalam";
    // institute.className = "institute"
    institute.style = "margin-left:5px; width:30%";
    institute.name = "institute";

    //Country
    const academic_country = document.createElement("select");
    academic_country.name = "academic_rec_country";
    academic_country.style = "width:15%; margin-left:5px; padding:8px 10px; background: #ddd; border: none;border-radius: 5px;";
    
    var select_country = new Option ('Country', 'Country');
    select_country.setAttribute('disabled' , '')
    select_country.setAttribute('selected', '')
    academic_country.appendChild(select_country)

    for (country in countryList){
        var country_list = new Option (countryList[country] , countryList[country]);
        academic_country.appendChild(country_list);
    }
    
    //date of award 
    const date_award = document.createElement("input");
    date_award.type = "date"
    date_award.style = "width:15%; margin-left:5px;"
    date_award.name = "date_award";
    //grades

    const grade = document.createElement("input");
    grade.type = "text";
    grade.style = "width:20%";
    grade.name = "grade";
    grade.placeholder = "Grade. Eg:First class Honour";

    //line
    const line = document.createElement("hr")


    const btn = document.createElement("a");
    btn.className = "delete";
    btn.innerHTML = "&times";

    btn.addEventListener("click", removeInput);

    const flex = document.createElement("div");
    flex.className = "flex";

    input.appendChild(flex);
    flex.appendChild(academic_name);
    flex.appendChild(institute);
    flex.appendChild(academic_country);
    flex.appendChild(date_award);
    flex.appendChild(grade);
    flex.appendChild(btn);
    flex.appendChild(line);
}
    

addBtn.addEventListener("click", addInput);

//membership fellowhsip
function addMembershipFellowship(){
  const membership_fellowship = document.createElement("input");
  membership_fellowship.type = "text";
  membership_fellowship.placeholder = "Membership or Fellowship";
  membership_fellowship.style = "width:95%";
  membership_fellowship.name =
    "membership_fellowship";

  const btn = document.createElement("a");
  btn.className = "delete";
  btn.innerHTML = "&times";

  btn.addEventListener("click", removeInput);

  const flex = document.createElement("div");
  flex.className = "flex";

  input_membership_fellowship.appendChild(flex);
  flex.appendChild(membership_fellowship);
  flex.appendChild(btn);

}

addBtn_membership_fellowhsip.addEventListener("click", addMembershipFellowship);

// inputs for employment record in higher education
function addErhe(){
  //row
  const row = document.createElement("div");
  row.className = "row"

  //col
  const col = document.createElement("div");
  col.className = "col";
  const col1 = document.createElement("div");
  col1.className = "col";
  const col2 = document.createElement("div");
  col2.className = "col";
  const col3 = document.createElement("div");
  col3.className = "col";
  const col4 = document.createElement("div");
  col4.className = "col";
  const col5 = document.createElement("div");
  col5.className = "col";


  //labels
  const label = document.createElement("label");
  label.innerHTML = "Position"
  const label1 = document.createElement("label");
  label1.innerHTML = "Previous Institution";
  const label2 = document.createElement("label");
  label2.innerHTML = "Country";
  const label3 = document.createElement("label");
  label3.innerHTML = "Start Date";
  const label4 = document.createElement("label");
  label4.innerHTML = "End Date";

  //group
  const group = document.createElement("group");
  group.className = "form-group";
  const group1 = document.createElement("group");
  group1.className = "form-group";
  const group2 = document.createElement("group");
  group2.className = "form-group";
  const group3 = document.createElement("group");
  group3.className = "form-group";
  const group4 = document.createElement("group");
  group4.className = "form-group";

  //position
  const academic_position = document.createElement("input");
  academic_position.type = "text";
  academic_position.placeholder = "Position";
  academic_position.name = "academic_position";
  academic_position.className = "form-control";
  academic_position.style = "width:355px;"

  //previous institution
  const prev_institution = document.createElement("input");
  prev_institution.type = "text";
  prev_institution.placeholder = "Previous Institution";
  prev_institution.style = "width:355px;";
  prev_institution.name = "prev_institute";
  prev_institution.className = "form-control";

  //country
  const erhe_country = document.createElement("select");
  erhe_country.name = "erhe_country";
  erhe_country.style =
    "padding:8px 10px; background: #ddd; border: none;border-radius: 5px; width:200px;";
  erhe_country.className = "form-control";

  var select_country = new Option("Country", "Country");
  select_country.setAttribute("disabled", "");
  select_country.setAttribute("selected", "");
  erhe_country.appendChild(select_country);

  for (country in countryList) {
    var country_list = new Option(countryList[country], countryList[country]);
    erhe_country.appendChild(country_list);
  }

  //start date
  const start_date = document.createElement("input");
  start_date.type = "date";
  start_date.style = "width:200px;";
  start_date.name = "start_erhe";
  start_date.className = "form-control";

  // end date
  const end_date = document.createElement("input");
  end_date.type = "date";
  end_date.style = "width:200px; ";
  end_date.name = "end_erhe";
  end_date.className = "form-control";

  const btn = document.createElement("button");
  btn.type="button";
  btn.innerHTML = "Delete";
  btn.className = "btn btn-danger";
  btn.style = "margin-top:20px; width:auto; background-color:red; height:45px; margin-right:70%";

  btn.addEventListener("click", removeInput);


  input_erhe.appendChild(row);
  row.appendChild(col);

  col.appendChild(group);
  group.appendChild(label);
  group.appendChild(academic_position);

  row.appendChild(col1);
  col1.appendChild(group1);
  group1.appendChild(label1);
  group1.appendChild(prev_institution);

  row.appendChild(col2);
  col2.appendChild(group2);
  group2.appendChild(label2);
  group2.appendChild(erhe_country);

  row.appendChild(col3);
  col3.appendChild(group3);
  group3.appendChild(label3);
  group3.appendChild(start_date);

  row.appendChild(col4);
  col4.appendChild(group4);
  group4.appendChild(label4);
  group4.appendChild(end_date);

  row.appendChild(btn);

  const line = document.createElement("hr");
  row.appendChild(line)
}

addBtn_erhe.addEventListener("click", addErhe );

//input fields in employment record in industry

function addEri(){
  //row
  const row = document.createElement("div");
  row.className = "row";

  //col
  const col = document.createElement("div");
  col.className = "col";
  const col1 = document.createElement("div");
  col1.className = "col";
  const col2 = document.createElement("div");
  col2.className = "col";
  const col3 = document.createElement("div");
  col3.className = "col";
  const col4 = document.createElement("div");
  col4.className = "col";
  const col5 = document.createElement("div");
  col5.className = "col";

  //labels
  const label = document.createElement("label");
  label.innerHTML = "Position";
  const label1 = document.createElement("label");
  label1.innerHTML = "Previous Industry Name";
  const label2 = document.createElement("label");
  label2.innerHTML = "Country";
  const label3 = document.createElement("label");
  label3.innerHTML = "Start Date";
  const label4 = document.createElement("label");
  label4.innerHTML = "End Date";

  //group
  const group = document.createElement("group");
  group.className = "form-group";
  const group1 = document.createElement("group");
  group1.className = "form-group";
  const group2 = document.createElement("group");
  group2.className = "form-group";
  const group3 = document.createElement("group");
  group3.className = "form-group";
  const group4 = document.createElement("group");
  group4.className = "form-group";

  //industry position
  const industry_position = document.createElement("input");
  industry_position.type = "text";
  industry_position.placeholder = "Position";
  industry_position.name = "industry_position";
  industry_position.className = "form-control";
  industry_position.style = "width:355px;"

  //previous industry name
  const industry_name = document.createElement("input");
  industry_name.type = "text";
  industry_name.placeholder = "Previous Industry Name";
  industry_name.style = "width:355px;";
  industry_name.name = "prev_industry";
  industry_name.className = "form-control";

  //country
  const eri_country = document.createElement("select");
  eri_country.name = "eri_country";
  eri_country.style =
    "width:200px; padding:8px 10px; background: #ddd; border: none;border-radius: 5px;";
  eri_country.className = "form-control"

  var select_country = new Option("Country", "Country");
  select_country.setAttribute("disabled", "");
  select_country.setAttribute("selected", "");
  eri_country.appendChild(select_country);

  for (country in countryList) {
    var country_list = new Option(countryList[country], countryList[country]);
    eri_country.appendChild(country_list);
  }

  //start date
  const start_date = document.createElement("input");
  start_date.type = "date";
  start_date.style = "width:200px";
  start_date.name = "start_eri";
  start_date.className = "form-control";

  //end date
  const end_date = document.createElement("input");
  end_date.type = "date";
  end_date.style = "width:200px";
  end_date.name = "end_eri";
  end_date.className = "form-control";

  const btn = document.createElement("button");
  btn.type = "button";
  btn.innerHTML = "Delete";
  btn.className = "btn btn-danger";
  btn.style =
    "margin-top:20px; width:auto; background-color:red; height:45px; margin-right:70%";

  btn.addEventListener("click", removeInput);

  input_eri.appendChild(row);
  row.appendChild(col);

  col.appendChild(group);
  group.appendChild(label);
  group.appendChild(industry_position);

  row.appendChild(col1);
  col1.appendChild(group1);
  group1.appendChild(label1);
  group1.appendChild(industry_name);

  row.appendChild(col2);
  col2.appendChild(group2);
  group2.appendChild(label2);
  group2.appendChild(eri_country);

  row.appendChild(col3);
  col3.appendChild(group3);
  group3.appendChild(label3);
  group3.appendChild(start_date);

  row.appendChild(col4);
  col4.appendChild(group4);
  group4.appendChild(label4);
  group4.appendChild(end_date);

  row.appendChild(btn);

  const line = document.createElement("hr");
  row.appendChild(line);
}

addBtn_eri.addEventListener("click", addEri);

function addCourse(){
  //course
  const course = document.createElement("input");
  course.type = "text";
  course.placeholder = "Course Name";
  course.name = "course" ;

  //level
  const level = document.createElement("select");
  level.name = "course_level";
  level.style =
    "width:15%; margin-left:5px; padding:8px 10px; background: #ddd; border: none;border-radius: 5px;";

  var option = new Option("Level", "Level");
  option.setAttribute("disabled", "");
  option.setAttribute("selected", "");
  var Undergraduate = new Option("Undergraduate", "Undergraduate");
  var Postgraduate = new Option("Postgraduate", "Postgraduate");

  level.appendChild(option);
  level.appendChild(Undergraduate);
  level.appendChild(Postgraduate);

  const btn = document.createElement("a");
  btn.className = "delete";
  btn.innerHTML = "&times";

  btn.addEventListener("click", removeInput);

  const flex = document.createElement("div");
  flex.className = "flex";

  input_courses.appendChild(flex);
  flex.appendChild(course);
  flex.appendChild(level);
  flex.appendChild(btn);
}

addBtn_courses.addEventListener("click", addCourse)

function addLanguage(){
  //row
  const row = document.createElement("div");
  row.className = "row";

  //col
  const col = document.createElement("div");
  col.className = "col";

  const col1 = document.createElement("div");
  col1.className = "col";

  //form-group
  const group = document.createElement("div");
  group.className = "form-group";
  const group1 = document.createElement("div");
  group1.className = "form-group";

  //label for language
  const label_1 = document.createElement("label");
  label_1.innerHTML = "Language";

  const label_2 = document.createElement("label");
  label_2.innerHTML = "Fluency";

  //input for language
  const language = document.createElement("input");
  language.type = "text";
  language.style = "width: 355px;";
  language.name = "language";
  language.className = "form-control";

  //select options for level of fluency
  const fluency = document.createElement("select");
  fluency.name = "fluency";
  fluency.className = "form-control";
  fluency.style = "width:355px";

  //option
  var option = new Option("---", "---");
  var fluent = new Option("Fluent", "Fluent");
  var good = new Option("Good", "Good");
  var fair = new Option("Fair", "Fair");

  fluency.appendChild(option);
  fluency.appendChild(fluent);
  fluency.appendChild(good);
  fluency.appendChild(fair);

  const btn = document.createElement("a");
  btn.className = "delete";
  btn.innerHTML = "&times";
  btn.style = "margin-top:30px;";

  btn.addEventListener("click", removeInput);

  input_language.appendChild(row);
  row.appendChild(col);
  col.appendChild(group);
  group.appendChild(label_1);
  group.appendChild(language);
  row.appendChild(col1);
  col1.appendChild(group1);
  group1.appendChild(label_2);
  group1.appendChild(fluency);
  row.appendChild(btn);
}

addBtn_language.addEventListener("click", addLanguage)

//add children

function addChildren(){
  var number = document.getElementById("no_children").value;
  var container = document.getElementById ("children_container");

  while (container.hasChildNodes()){
    container.removeChild(container.lastChild);
  }

  for (i=0;i<number;i++){
    container.appendChild(document.createTextNode("Child " + (i + 1)));

    //name
    var name = document.createElement("input");
    name.type = "text";
    name.name = "children_name";
    name.placeholder = "Child's name";
    name.style = "margin-left:10px; margin-right:5px;";

    //dob
    var dob = document.createElement("input");
    dob.type = "date";
    dob.name = "children_dob";
    dob.style = "margin-left:5px;";

    //gender
    var gender = document.createElement("select");
    gender.name = "children_gender";
    gender.style = "width:15%; margin-left:5px; padding:8px 10px; background: #ddd; border: none;border-radius: 5px;";

    //options for gender
    var option = new Option ("gender" , "gender");
    option.setAttribute("disabled", "");
    option.setAttribute("selected", "");

    var male = new Option ("Male", "Male");
    var female = new Option("Female", "Female");

    gender.appendChild(option);
    gender.appendChild(male);
    gender.appendChild(female);


    container.appendChild(name);
    container.appendChild(document.createTextNode("Date of Birth"));
    container.appendChild(dob);
    container.appendChild(gender);
    // Append a line break
    container.appendChild(document.createElement("br"));
  }
}

addBtn_children.addEventListener("click", addChildren)

//Date of any previous application .. yes or no option, if yes -> date input for previous application
function prevApplication(){
  
}

