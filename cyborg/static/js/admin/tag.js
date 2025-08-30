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

    addTag(tag) {
        if (this.tags.includes(tag)) {
            this.showDuplicate(tag);
        } else {
            this.tags.push(tag);
            this.createTagElement(tag);
        }
        this.input.value = '';
    }

    deleteTag(index) {
        if (index >= 0 && index < this.tags.length) {
            this.tags.splice(index, 1);
            this.renderTags();
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
        this.shadowRoot.querySelectorAll('.tag').forEach(el => el.remove());
        this.tags.forEach(this.createTagElement.bind(this));
    }
}

customElements.define('rbl-tag-input', RblTagInput);