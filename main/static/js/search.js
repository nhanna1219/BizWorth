document.addEventListener('DOMContentLoaded', function () {
    const inputField = document.querySelector('.chosen-value');
    const dropdown = document.querySelector('.value-list');
    const dropdownArray = [...document.querySelectorAll('.tickers')];
    
    let valueArray = [];
    dropdownArray.forEach(item => {
        valueArray.push(item.textContent);
    });

    const closeDropdown = () => {
        dropdown.classList.remove('open');
    }

    inputField.addEventListener('input', (e) => {
        let inputValue = inputField.value.toLowerCase();
        if (inputValue.length > 0) {
            dropdown.classList.add('open');
            inputField.style = "border-radius:15px 15px 0 0;"
            for (let j = 0; j < valueArray.length; j++) {
                if (valueArray[j].toLowerCase().indexOf(inputValue) === -1) {
                    dropdownArray[j].classList.add('closed');
                } else {
                    dropdownArray[j].classList.remove('closed');
                }
            }
        } else {
            for (let i = 0; i < dropdownArray.length; i++) {
                dropdownArray[i].classList.remove('closed');
            }
        }
    });

    // Click on Ticker Event
    dropdownArray.forEach(item => {
        item.addEventListener('click', (evt) => {
            inputField.value = item.textContent;
            dropdownArray.forEach(dropdown => {
                dropdown.classList.add('closed');
            });
            document.getElementById('valuation').scrollIntoView();
        });
    })

    inputField.addEventListener('focus', () => {
        inputField.placeholder = 'Type to filter...';
        inputField.style = "border-radius:15px 15px 0 0;"
        dropdown.classList.add('open');
        dropdownArray.forEach(dropdown => {
            dropdown.classList.remove('closed');
        });
        this.body.classList.add('overlay');
    });

    inputField.addEventListener('blur', () => {
        inputField.style = "";
        inputField.placeholder = 'Choose Your Ticker';
        if (inputField.value.trim() !== "")
            inputField.style = "font-weight: 600;";
        closeDropdown();
    });

});
