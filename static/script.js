
const recipientInput = document.getElementById('recipient-input');
const addButton = document.getElementById('add');
const recipients = document.getElementById('Recipients');
const removeButton = document.getElementById('remove');

addButton.addEventListener('click', addRecipient);
removeButton.addEventListener('click', removeRecipient);


function updateContent(section) {
    window.location.href = section;
}

function addRecipient() {
    const recipientValue = recipientInput.value.trim();

    if (recipientValue !== '') {
        const option = document.createElement('option');
        option.value = recipientValue;
        option.text = recipientValue;

        recipients.add(option);
        recipientInput.value = '';
    }
}
function removeRecipient() {
    recipients.selectedOptions[0].remove();
}