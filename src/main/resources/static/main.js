window.onload = () => {
    console.log("CIAO");

    const searchBtn = document.getElementById("searchBtn");
    const searchText = document.getElementById("searchText");
    const resultList = document.getElementById("resultList");

    const createAccordion = function(solrDocument) {
        const accordionItem = document.createElement("div");
        accordionItem.classList.add("accordion-item");
        const id = `collapse_${solrDocument.ID}`;

        accordionItem.innerHTML = `<h2 class="accordion-header">
          <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#${id}" aria-expanded="false" aria-controls="${id}">
            ${solrDocument.titolo}
          </button>
        </h2>
        <div id="${id}" class="accordion-collapse collapse" data-bs-parent="#resultList">
          <div class="accordion-body">
            ${solrDocument.introduzione}
          </div>
          <p><a href="${solrDocument.url}">Link</a></p>
        </div>`;

        return accordionItem;
    };

    const appendDocument = function(solrDocument) {
        const accordion = createAccordion(solrDocument);
        resultList.appendChild(accordion);
    };

    searchBtn.addEventListener("submit", null);
    searchBtn.addEventListener("click", async (event) => {
        event.preventDefault();

        resultList.innerHTML = '';

        let response = await fetch(
            'http://localhost:8080/hello',
            {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: searchText.value,
                    boost_title: 2,
                    boost_intro: 3,
                    boost_content: 1
                })
            }
        );
        let result = await response.json();
        console.log(result);

        result.forEach(appendDocument);
    });
}