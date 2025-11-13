// In a static/js/taggit_select2_init.js file

class RblTagInput extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.tags = [];
        this.allowDelete = false;
    }

    connectedCallback() {
        this.render();
        
        // 🛑 FIX: Use requestAnimationFrame to defer the query until the Light DOM is attached.
        window.requestAnimationFrame(() => {
            // Get the reference to the actual form field which is a direct child of the host element.
            this.formInput = this.querySelector('input[name], textarea[name]');
    
            if (!this.formInput) {
                 // You can remove this console.error if the fix works, but keep it for now.
                 console.error("RblTagInput: Could not find the inner form input to update its value. (Deferred Check Failed)", this);
                 return; 
            }
            
            // 💡 INITIALIZE TAGS: Initialize internal tags from existing value in the form input
            if (this.formInput.value) {
                // Split by comma and trim whitespace to get initial tags
                this.tags = this.formInput.value.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0);
                // Call renderTags to both draw the tags AND update the form value
                this.renderTags(); 
            }
        });
    }

    render() {
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    font-family: 'Helvetica Neue', 'Lucida Grande', sans-serif;
                    max-width: 100%;
                    display: flex;
                    align-content: flex-start;
                    flex-wrap: wrap;
                    background-color: #FFF;
                    border: solid 1px #CCC;
                    border-radius: 2px;
                    min-height: 33px;
                    padding: 0 5px;
                }

                #tag-input {
                    flex-grow: 1;
                    display: inline-block;
                    order: 200;
                    border: none;
                    height: 33px;
                    line-height: 33px;
                    font-size: 14px;
                    margin: 0;
                }

                #tag-input:focus {
                    outline: none;
                }

                .tag {
                    display: inline-block;
                    flex-grow: 0;
                    margin: 5px 5px 5px 0;
                    padding: 0 10px;
                    height: 25px;
                    line-height: 25px;
                    background-color: #E1E1E1;
                    color: #333;
                    font-size: 14px;
                    order: 100;
                    border-radius: 2px;
                    position: relative;
                    overflow: hidden;
                }

                .tag.duplicate {
                    background-color: rgba(255, 64, 27, 0.71);
                    transition: all 0.3s linear;
                }

                .tag:last-child {
                    margin-right: 5px;
                }

                .tag .remove {
                    display: inline-block;
                    background-color: rgba(255, 64, 27, 0.71);
                    color: #FFF;
                    position: absolute;
                    right: -20px;
                    width: 20px;
                    text-align: center;
                    border-top-right-radius: 2px;
                    border-bottom-right-radius: 2px;
                    transition: all 0.3s ease;
                    cursor: pointer;
                }

                .tag:hover .remove {
                    right: 0;
                }
            </style>
            <input type="text" id="tag-input" />
        `;

        this.input = this.shadowRoot.getElementById('tag-input');
        this.input.addEventListener('keydown', this.handleKeyDown.bind(this));
    }

    handleKeyDown(event) {
        const tagValue = this.input.value.trim();

        if (event.key === 'Enter' || event.key === ',') {
            event.preventDefault();
            if (tagValue) {
                this.addTag(tagValue);
            }
        } else if (event.key === 'Backspace' && tagValue.length === 0) {
            if (this.allowDelete) {
                this.deleteLastTag();
                this.allowDelete = false;
            } else {
                this.allowDelete = true;
            }
        }
    }

    updateFormValue() {
        const commaSeparatedTags = this.tags.join(', ');
    
        if (this.formInput) {
            // 🛑 Update the value of the actual form input
            this.formInput.value = commaSeparatedTags; 
            
            // Trigger a 'change' event to notify Django/FormSet listeners
            this.formInput.dispatchEvent(new Event('change', { bubbles: true }));
        } else {
            console.error("RblTagInput: Could not find the inner form input to update its value.");
        }
    }

    // addTag(tag) {
    //     if (this.tags.includes(tag)) {
    //         this.showDuplicate(tag);
    //     } else {
    //         this.tags.push(tag);
    //         this.createTagElement(tag);
    //     }
    //     this.input.value = '';
    // }

    // deleteTag(index) {
    //     if (index >= 0 && index < this.tags.length) {
    //         this.tags.splice(index, 1);
    //         this.renderTags();
    //     }
    // }

    addTag(tag) {
        if (this.tags.includes(tag)) {
            this.showDuplicate(tag);
        } else {
            this.tags.push(tag);
            this.createTagElement(tag);
            this.updateFormValue(); // <-- NEW
        }
        this.input.value = '';
    }

    deleteTag(index) {
        if (index >= 0 && index < this.tags.length) {
            this.tags.splice(index, 1);
            this.renderTags();
            this.updateFormValue(); // <-- NEW
        }
    }

    deleteLastTag() {
        if (this.tags.length > 0) {
            this.deleteTag(this.tags.length - 1);
        }
    }

    showDuplicate(tag) {
        const index = this.tags.indexOf(tag);
        const tagElement = this.shadowRoot.querySelector(`[data-index="${index}"]`);
        if (tagElement) {
            tagElement.classList.add('duplicate');
            setTimeout(() => {
                tagElement.classList.remove('duplicate');
            }, 500);
        }
    }

    createTagElement(tag) {
        const tagElement = document.createElement('div');
        tagElement.className = 'tag';
        tagElement.textContent = tag;

        const removeButton = document.createElement('span');
        removeButton.className = 'remove';
        removeButton.textContent = '×';
        removeButton.addEventListener('click', () => {
            const index = this.tags.indexOf(tag);
            this.deleteTag(index);
        });

        tagElement.appendChild(removeButton);
        tagElement.dataset.index = this.tags.indexOf(tag);

        this.shadowRoot.insertBefore(tagElement, this.input);
    }

    renderTags() {
        // First, clear all existing tag UI elements from the Shadow DOM
        this.shadowRoot.querySelectorAll('.tag').forEach(el => el.remove());
        // Then, render the tags from the internal array
        this.tags.forEach(this.createTagElement.bind(this));
        
        // 💡 IMPORTANT: Update the form value after rendering tags during initialization
        // This is only strictly needed if you are editing an existing item and the tags array was just populated.
        this.updateFormValue();
    }
}

customElements.define('rbl-tag-input', RblTagInput);