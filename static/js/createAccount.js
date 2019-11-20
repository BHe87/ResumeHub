function Student(id, username, pwHash, firstName, lastName, organizations, year, major, minor, resume, gender, gpa, phoneNumber) {

}

function Organization(id, username, pwHash, name, description) {

}

function Company(id, username, pwHash, name, description, sponsorID) {

}

function createAccount(form) {
	console.log("creating a new account");

	var accountTypes = form.elements["accountType"];
	var accountType = "";
	for (var i = 0; i < accountTypes.length; i++) {
		if (accountTypes[i].checked) {
			accountType = accountTypes[i].value;
			console.log("account type selected: " + accountType);
		}
	}
	if (accountType == "Student") {
		var student = {id:"", username:"", pwHash:"", firstName:"", lastName:"", organizations:"", year:"", major:"", minor:"", resume:"", gender:"", gpa:"", phoneNumber:""};
		//populate student data from the form and save in db
	}
}