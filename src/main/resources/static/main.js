window.onload = () => {
    const searchBtn = document.getElementById("searchBtn");
    const searchText = document.getElementById("searchText");
    const resultList = document.getElementById("resultList");

    const createListGroupElement = function (path, i) {
        const category = path[0].charAt(0).toUpperCase() + path[0].slice(1);
        const ul = document.createElement("ul");
        ul.classList.add("list-group");
        const li = document.createElement("li");
        li.classList.add("list-group-item");
        const h =  document.createElement("h3");
        h.innerHTML = `<h${i}>${category}</h${i}>`
        li.appendChild(h);

        if (path.slice(1).length > 0) {
            li.appendChild(createListGroupElement(path.slice(1), i+1));
        }

        ul.appendChild(li);
        return ul;
    };

    window.clickedCategory = function(category) {
        const url = new URL('http://localhost:8080/path');
        url.search = new URLSearchParams({'category': category}).toString();
        fetch(url).then(response => response.json()).then(paths => {
            const categoryList = document.getElementById("categoryList");
            categoryList.innerHTML = '<div id="categoryList"></div>'
            for (let path of paths) {
                const list = createListGroupElement(path, 3);
                categoryList.appendChild(list);
            }
        });
    }

    // utility function
    const createTagList = function(tags) {
        let result = "";
        for (let s of tags) {
            result += `<span class="tag" onclick="clickedCategory('${s}');">${s}</span>`;
        }
        return result;
    }

    const createAccordion = function(solrDocument) {
        const accordionItem = document.createElement("div");
        accordionItem.classList.add("accordion-item");
        const id = `collapse_${solrDocument.ID}`;

        accordionItem.innerHTML = `<h2 class="accordion-header">
          <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#${id}" aria-expanded="false" aria-controls="${id}">
            <b>${solrDocument.titolo}</b>
          </button>
        </h2>
        <div id="${id}" class="accordion-collapse collapse" data-bs-parent="#resultList">
          <div class="accordion-body">
            <p>
                <b>Categorie:</b> ${createTagList(solrDocument.categorie)}.
            </p><br>
            <p>
                ${solrDocument.introduzione}
            </p>
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
        console.log("FETCH");
        let response = await fetch(
            'http://localhost:8080/query',
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