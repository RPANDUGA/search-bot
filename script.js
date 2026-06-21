// Sample database of searchable content
const DATABASE = [
    {
        title: "Introduction to JavaScript",
        description: "Learn the basics of JavaScript programming language",
        category: "Programming",
        link: "#"
    },
    {
        title: "Web Development Best Practices",
        description: "Essential tips and tricks for building modern web applications",
        category: "Web Development",
        link: "#"
    },
    {
        title: "CSS Grid Tutorial",
        description: "Master CSS Grid layout system with practical examples",
        category: "CSS",
        link: "#"
    },
    {
        title: "Python for Data Science",
        description: "Comprehensive guide to using Python in data science projects",
        category: "Data Science",
        link: "#"
    },
    {
        title: "REST API Design Guide",
        description: "Best practices for designing RESTful APIs",
        category: "API Design",
        link: "#"
    },
    {
        title: "React Hooks Explained",
        description: "Deep dive into React Hooks and state management",
        category: "React",
        link: "#"
    },
    {
        title: "Database Optimization",
        description: "Techniques to optimize database performance and queries",
        category: "Database",
        link: "#"
    },
    {
        title: "Machine Learning Basics",
        description: "Introduction to machine learning concepts and algorithms",
        category: "Machine Learning",
        link: "#"
    },
    {
        title: "Git Version Control",
        description: "Master Git and GitHub for collaborative development",
        category: "DevOps",
        link: "#"
    },
    {
        title: "Node.js Server Development",
        description: "Build scalable server applications with Node.js",
        category: "Backend",
        link: "#"
    }
];

// DOM Elements
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const resultsContainer = document.getElementById('resultsContainer');
const resultsList = document.getElementById('resultsList');
const resultsInfo = document.getElementById('resultsInfo');
const noResults = document.getElementById('noResults');
const loading = document.getElementById('loading');

// Event Listeners
searchBtn.addEventListener('click', performSearch);
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        performSearch();
    }
});

// Search Function
function performSearch() {
    const query = searchInput.value.trim();
    
    if (!query) {
        alert('Please enter a search query');
        return;
    }

    showLoading(true);
    
    // Simulate API delay
    setTimeout(() => {
        const results = searchDatabase(query);
        displayResults(results, query);
        showLoading(false);
    }, 500);
}

// Search Database
function searchDatabase(query) {
    const lowerQuery = query.toLowerCase();
    
    return DATABASE.filter(item => {
        const titleMatch = item.title.toLowerCase().includes(lowerQuery);
        const descriptionMatch = item.description.toLowerCase().includes(lowerQuery);
        const categoryMatch = item.category.toLowerCase().includes(lowerQuery);
        
        return titleMatch || descriptionMatch || categoryMatch;
    }).sort((a, b) => {
        // Prioritize title matches
        const aTitle = a.title.toLowerCase().includes(lowerQuery);
        const bTitle = b.title.toLowerCase().includes(lowerQuery);
        
        if (aTitle && !bTitle) return -1;
        if (!aTitle && bTitle) return 1;
        return 0;
    });
}

// Display Results
function displayResults(results, query) {
    resultsList.innerHTML = '';
    resultsContainer.classList.remove('hidden');
    noResults.classList.add('hidden');
    
    if (results.length === 0) {
        resultsContainer.classList.add('hidden');
        noResults.classList.remove('hidden');
        return;
    }
    
    resultsInfo.textContent = `Found ${results.length} result${results.length !== 1 ? 's' : ''} for "${query}"`;
    
    results.forEach(result => {
        const resultElement = createResultElement(result, query);
        resultsList.appendChild(resultElement);
    });
}

// Create Result Element
function createResultElement(result, query) {
    const div = document.createElement('div');
    div.className = 'result-item';
    
    // Highlight matching text
    const highlightedTitle = highlightText(result.title, query);
    const highlightedDescription = highlightText(result.description, query);
    
    div.innerHTML = `
        <div class="result-title">${highlightedTitle}</div>
        <div class="result-description">${highlightedDescription}</div>
        <small style="color: #999; margin-top: 10px; display: block;">Category: ${result.category}</small>
        <a href="${result.link}" class="result-link">Learn more →</a>
    `;
    
    return div;
}

// Highlight matching text
function highlightText(text, query) {
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<mark style="background-color: #fff3cd; padding: 2px 4px; border-radius: 3px;">$1</mark>');
}

// Show/Hide Loading
function showLoading(isLoading) {
    if (isLoading) {
        loading.classList.remove('hidden');
        resultsContainer.classList.add('hidden');
        noResults.classList.add('hidden');
    } else {
        loading.classList.add('hidden');
    }
}

// Focus search input on page load
searchInput.focus();
