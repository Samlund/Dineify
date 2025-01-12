document.getElementById("generator_btn").addEventListener('click', generatorBtn);

/**
 * Validation when user pressed the button "Enter" and sends request to backend
 * @returns {Promise<void>}
 */
async function generatorBtn() {
    try {
        const selectedCuisine = getSelectedCuisine();

        if (!selectedCuisine || selectedCuisine === "Open to select cuisine") {
            alert('Please select cuisine.');
            return;
        }

        var hideContent = document.getElementById("generated_content");
        hideContent.style.display = "none";

        const recipes = await fetchRecipes(selectedCuisine);
        const id = await fetchId(selectedCuisine);
        displayRecipe(recipes.menu);
        displayPlaylist(id);

        hideContent.style.display = "block";

    } catch (error) {
        console.error("Error fetching recipes:", error);
        alert("Please try again");
    }
}

/**
 * Get selected cuisine
 * @returns The cuisine selected in dropdown menu
 */
function getSelectedCuisine() {
    const cuisineSelection = document.querySelector("#search_generator select");
    return cuisineSelection.value;
}

/**
 * Sends request to the backend to get recipes
 * @param cuisine Query the request will be based on
 * @returns JSON object containing the generated recipes
 */
async function fetchRecipes(cuisine) {
    const header = new Headers();
        header.append("Accept", "application/json");
    try {
        const response = await fetch(`/v1.0/recipes/?cuisine=${cuisine}`, {
            headers: header
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error("Fetch error:", error);
        throw error;
    }
}

/**
 * Sends request to the backend to get a playlist ID
 * @param cuisine Query the request will be based on
 * @returns {Promise<any>} JSON object containing the id as a string
 */
async function fetchId(cuisine) {
    const header = new Headers();
        header.append("Accept", "application/json");
    try {
        const response = await fetch(`/v1.0/playlists/?theme=${cuisine}`, {
            headers: header
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error("Fetch error:", error);
        throw error;
    }
}

/**
 * Assign content to correct HTML element
 * @param dishes JSON object containing the dishes that are to be displayed
 */
function displayRecipe(dishes) {
    dishes.forEach(recipe => {
        const courseDiv = document.getElementById(`course_${recipe.course}`);
        if (courseDiv) {
            generateCourse(courseDiv, recipe);
        } else {
            console.warn(`Course_${recipe.course} could not be found.`);
        }
    });
}

/**
 * Update the src of the embedded player to show the provided playlist
 * @param id id of the playlist
 */
function displayPlaylist(id) {
    document.getElementById("embedded_player").src = `https://open.spotify.com/embed/playlist/${id}?utm_source=generator`;
}

/**
 * Adds content to assigned element
 * @param courseDiv element to populate
 * @param recipe recipe to be added to the element
 */
function generateCourse(courseDiv, recipe) {
    const accordionHeader = courseDiv.closest(".accordion-item").querySelector(".accordion-header button");
    const header = courseDiv.querySelector(`#${recipe.course}_header`);
    const img = courseDiv.querySelector(`#${recipe.course}_img`);
    const ingredients = courseDiv.querySelector(`#${recipe.course}_ingredients`);
    const instructions = courseDiv.querySelector(`#${recipe.course}_instructions`);
    const summary = courseDiv.querySelector(`#${recipe.course}_summary`);

    if (accordionHeader) {
        accordionHeader.innerHTML = `${accordionHeader.textContent.trim()} ${recipe.title}`;
    } else {
        console.warn(`${recipe.course} was not found.`);
    }

    if (header) {
        header.innerHTML = `Course: ${recipe.course} <br> Servings: ${recipe.servings} <br> Ready in: ${recipe.readyInMinutes} minutes <br> URL: <a href="${recipe.url}">${recipe.url}</a>`;
    } else {
        console.warn(`${recipe.course}_header was not found.`);
    }

    if (img) {
        img.src = recipe.image;
        img.alt = `${recipe.course} image`;
    } else {
        console.warn(`${recipe.course}_img was not found.`);
    }

    if (ingredients) {
        ingredients.innerHTML = `<h4>Ingredients</h4>${recipe.ingredients.map(ing => `${ing.amount} ${ing.unit} ${ing.name}`).join('<br>')}`;
    } else {
        console.warn(`${recipe.course}_ingredients was not found.`);
    }

    if (instructions) {
        instructions.innerHTML = `<h4>Instructions</h4>${recipe.instructions}`;
    } else {
        console.warn(`${recipe.course}_instructions was not found.`);
    }

    if (summary) {
        summary.innerHTML = `<h4>Summary</h4>${recipe.summary}`;
    } else {
        console.warn(`${recipe.course}_summary was not found.`);
    }
}
