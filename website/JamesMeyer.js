// ############## start of document ready function ###################
// This function is to run the JavaScript code once the page is loaded.
// If you already have such a function just call the SetupTips function
// from your document ready function.

// Revised Nov 2021


document.addEventListener("DOMContentLoaded", function () {

	SetupTips();

});
// ############## end of document ready function ####################

// ###### Tooltips function which includes setup of footnotes #######
function SetupTips() {

	var fnNumber = 0;
	var myid = '';
	var clsStart, clsEnd;
	var myClassList, myClass;
	var baseHide, baseFn;
	var myFn, i = 0, j = 0, len, clL;

	try {

		var fnotes = document.querySelectorAll('span[class^=footnote]');
		// the footnotes = all spans which include a class name that begins with "footnote"

		for (i = 0, len = fnotes.length; i < len; i++) {
			myFn = fnotes[i];
			myClassList = myFn.classList;
			for (j = 0, clL = myClassList.length; j < clL; j++) {
				myClass = myClassList[j];

					if (clsEnd !== myClass.substr(8)) { // then we have a new footnotes section
						clsEnd = myClass.substr(8); // this identifies the section
						// add a hidden link to skip the section
						document.getElementById('Footnotes' + clsEnd).insertAdjacentHTML('beforebegin', '<a href="#Footnotes' + clsEnd + '-End"><span class="invis">Skip footnote section</span></a>');
						// add the hidden div to where that link goes to
						document.getElementById('Footnotes' + clsEnd).insertAdjacentHTML('afterend', '<div class="invis" id="Footnotes' + clsEnd + '-End"></div>');
					}

				// now do the footnotes
				clsStart = myClass.substr(0, 8);
				if (clsStart === 'footnote') { // we have a footnote
					fnNumber = i + 1; // array starts with 0; we want notes to start with 1
					myid = 'Fn_' + fnNumber + '_' + clsEnd; // unique footnote reference

					myFn.id = myid; //set the id of the footnote
					myFn.classList.add('hideTip'); // hide the footnote in the text
					myFn.classList.add('tipContent'); // add class for styling the tooltip
					myFn.setAttribute('role', 'note'); //add ARIA attribute for accessibility

					// add the footnote reference to the text
					myFn.insertAdjacentHTML('beforebegin', '<sup class="fnNum"><a href="#%20Show%20Footnote%20' + fnNumber + ' " title="Show/Hide footnote ' + fnNumber + ' " id="' + myid + 'a" onclick="showHide(&quot;' + myid + '&quot;);return false;">[<span class="invis">Footnote </span><span class="fnNumIn">' + fnNumber + '</span>]</a></sup>');

					// insert footnote number and the footnote where the footnotes are required to appear
					document.getElementById('Footnotes' + clsEnd).innerHTML += '<p><span class="fnNumBase"><a href="#' + myid + 'a" title="Footnote location">[<span class="invis">Location of footnote </span><span class="fnNumIn">' + fnNumber + '</span>]</a> </span><span role="note" id="' + myid + 'Base" class="fnTextBase">' + myFn.innerHTML + '</span></p>';

					myFn.classList.remove(myClass); // remove extraneous stuff from the footnote tooltip
					myFn.getElementsByClassName('fnHide')[0].insertAdjacentHTML('afterend', fnNumber + ': '); // add the footnote number to the tooltip

					// remove the "hidden" (Footnote: and ) opening and closing tags of the footnotes in the collective section
					baseFn = document.getElementById(myid + 'Base');
					baseHide = baseFn.getElementsByClassName('fnHide');
					while (baseHide[0]) {
						baseFn.removeChild(baseHide[0]);
					}
				}
			}
		}

		// Make the appropriate parts of the footnotes invisible except to screen readers
		var fnHides = document.getElementsByClassName('fnHide');
		[].forEach.call(fnHides, function (el) {
			el.classList.add('invis');
		});

	} // end of try
	catch (e) {
		//catch and just suppress error
		// alert("fn: " + e);
	}
}
// ################# End of Tooltips function ######################

// ############## Function to set up showing or hiding of text #######
function showHide(divID) {
	var myDiv = document.getElementById(divID);
	try {
		if (myDiv.classList.contains('hideTip')) {
				myDiv.classList.remove('hideTip');
				myDiv.classList.add('unhideTip');
				if (divID.substr(0, 3) === 'Fn_') {
					// For if tip is a footnote replace number with an x
					document.getElementById(divID + 'a').innerHTML = '[<span class="fnNumIn">&#x2716;</span>]';
				}
		} else {
				myDiv.classList.remove('unhideTip');
				myDiv.classList.add('hideTip');
				if (divID.substr(0, 3) === 'Fn_') {
					// For if tip is a footnote, restore the reference number
					document.getElementById(divID + 'a').innerHTML = '[<span class="invis">Footnote </span><span class="fnNumIn">' + divID.substr(3).split('_')[0] + '</span>]';
				}
		}
	}
	catch (e) {
		// alert(e);
	}
}
// ######## End of function to set up showing or hiding of text #######