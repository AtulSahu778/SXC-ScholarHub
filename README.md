# SXC ScholarHub

SXC ScholarHub is a full-stack web application for St. Xavier's College, designed to centralize academic resources such as study materials, previous year papers, and more. It features robust authentication, role-based access (admin/student), resource upload/download, and advanced search/filtering.

---

## Features

- **User Authentication**: Register/login with JWT-based authentication. Admin and student roles supported.
- **Admin Resource Upload**: Only admins can upload new resources (notes, papers, assignments, etc.).
- **Student Access**: All students can browse, search, and download resources.
- **Advanced Search & Filter**: Search by title, subject, description, department, year, and type.
- **Resource Management**: Admins can delete resources. All uploads are attributed to the uploader.
- **Responsive UI**: Built with Next.js, Tailwind CSS, and Radix UI for a modern, mobile-friendly experience.
- **MongoDB Backend**: All data is stored in MongoDB, with secure connection and data validation.

---

## Project Structure

```
SXC-ScholarHub/
├── app/                # Next.js app directory
│   ├── api/            # API routes (RESTful endpoints)
│   ├── globals.css     # Global styles (Tailwind, custom CSS)
│   ├── layout.js       # Root layout
│   └── page.js         # Main page (UI, logic)
├── components/         # Reusable UI components (Radix UI, custom)
│   └── ui/             # UI primitives (Button, Card, Dialog, etc.)
├── hooks/              # Custom React hooks
├── lib/                # Utility functions
├── tests/              # Python test files (if any)
├── package.json        # Project dependencies and scripts
├── tailwind.config.js  # Tailwind CSS configuration
├── postcss.config.js   # PostCSS configuration
├── jsconfig.json       # JS/TS config for path aliases
└── ...
```

---

## Getting Started

### Prerequisites
- Node.js (v18+ recommended)
- MongoDB database (local or Atlas)

### Installation
1. **Clone the repository:**
   ```sh
git clone https://github.com/AtulSahu778/SXC-ScholarHub.git
cd SXC-ScholarHub
   ```
2. **Install dependencies:**
   ```sh
npm install
   ```
3. **Configure environment variables:**
   - Create a `.env.local` file in the root directory.
   - Add your MongoDB connection string:
     ```env
MONGO_URL=your_mongodb_connection_string
     ```

### Running the App
```sh
npm run dev
```
The app will be available at [(https://sxchub.vercel.app/)].

---

## Usage
- **Register/Login:** Create an account or log in. The first admin can be set by email (see code for details).
- **Browse Resources:** Use the search and filter options to find resources.
- **Upload Resource:** (Admins only) Click 'Upload Resource', fill the form, and submit.
- **Download Resource:** Click the download icon on any resource card.

---

## API Overview
- All API routes are under `/api/` and handled in `app/api/[[...path]]/route.js`.
- Endpoints include:
  - `POST /api/auth/register` — Register user
  - `POST /api/auth/login` — Login
  - `GET /api/resources` — List all resources
  - `POST /api/resources` — Upload resource (admin only)
  - `DELETE /api/resources/:id` — Delete resource (admin only)
  - `GET /api/resources/:id/download` — Download resource
  - `GET /api/users` — List users (admin only)
  - `GET /api/search` — Search resources

---

## Technologies Used
- **Frontend:** Next.js, React, Tailwind CSS, Radix UI, Lucide Icons
- **Backend:** Next.js API routes, MongoDB, JWT (custom, demo only)
- **Other:** Class variance authority, Tailwind Merge, etc.

---

## Customization
- **Theme:** Easily switch between light/dark mode (see `globals.css` and Tailwind config).
- **Departments/Years/Types:** Update the lists in `app/page.js` as needed.

---

## Testing
- Backend API is tested and verified (see `test_result.md`).
- Frontend testing is not included by default.

---

## License
MIT License. See [LICENSE](LICENSE) for details.

---

## Credits
Developed by Atul Sahu and AI.

---

## Contact
For issues or contributions, open an issue or pull request on GitHub.
