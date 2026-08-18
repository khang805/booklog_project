import { useState, useEffect } from "react";
import axios from "axios";

const API_URL = "http://localhost:8000/books/";

function App() {
  const [books, setBooks] = useState([]);
  const [form, setForm] = useState({ title: "", author: "", rating: 5 });

  // 1. Fetch all books from FastAPI (GET)
  const fetchBooks = async () => {
    try {
      const response = await axios.get(API_URL);
      setBooks(response.data);
    } catch (error) {
      console.error("Error fetching books:", error);
    }
  };

  useEffect(() => {
    fetchBooks();
  }, []);

  // 2. Add a new book (POST)
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.title || !form.author) return;

    try {
      await axios.post(API_URL, {
        title: form.title,
        author: form.author,
        rating: Number(form.rating),
      });
      setForm({ title: "", author: "", rating: 5 });
      fetchBooks(); // Refresh book list
    } catch (error) {
      console.error("Error adding book:", error);
    }
  };

  // 3. Delete a book by ID (DELETE)
  const handleDelete = async (id) => {
    try {
      await axios.delete(`${API_URL}${id}`);
      fetchBooks(); // Refresh book list
    } catch (error) {
      console.error("Error deleting book:", error);
    }
  };

  return (
    <div style={{ maxWidth: "600px", margin: "40px auto", fontFamily: "sans-serif" }}>
      <h1>📚 BookLog</h1>

      {/* Add Book Form */}
      <form onSubmit={handleSubmit} style={{ marginBottom: "20px", display: "flex", gap: "10px", flexWrap: "wrap" }}>
        <input
          type="text"
          placeholder="Title"
          value={form.title}
          onChange={(e) => setForm({ ...form, title: e.target.value })}
          required
        />
        <input
          type="text"
          placeholder="Author"
          value={form.author}
          onChange={(e) => setForm({ ...form, author: e.target.value })}
          required
        />
        <select
          value={form.rating}
          onChange={(e) => setForm({ ...form, rating: e.target.value })}
        >
          {[1, 2, 3, 4, 5].map((num) => (
            <option key={num} value={num}>
              {num} ⭐
            </option>
          ))}
        </select>
        <button type="submit">Add Book</button>
      </form>

      {/* Book List */}
      <ul style={{ listStyle: "none", padding: 0 }}>
        {books.map((book) => (
          <li
            key={book.id}
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              padding: "10px",
              borderBottom: "1px solid #ccc",
            }}
          >
            <div>
              <strong>{book.title}</strong> by {book.author} — {book.rating} ⭐
            </div>
            <button onClick={() => handleDelete(book.id)} style={{ color: "red" }}>
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
