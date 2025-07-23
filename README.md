# SXC ScholarHub

SXC ScholarHub is a full-stack web application for St. Xavier's College, designed to centralize academic resources such as study materials, previous year papers, and more. It features robust authentication, role-based access (admin/student), resource upload/download, advanced search/filtering, a Smart Academic Dashboard, dark theme, bookmark system, download tracking, and enhanced accessibility.

---

## Features

- **User Authentication**: Register/login with JWT-based authentication. Admin and student roles supported.
- **Admin Resource Upload**: Only admins can upload new resources (notes, papers, assignments, etc.).
- **Student Access**: All students can browse, search, and download resources.
- **Advanced Search & Filter**: Search by title, subject, description, department, year, and type.
- **Resource Management**: Admins can delete resources. All uploads are attributed to the uploader.
- **Smart Academic Dashboard**: Personalized dashboard for students and admins. Students see total downloads, recent resources, bookmarks, and trending materials. Admins see total uploads, recent uploads, and pending requests.
- **Bookmark System**: Users can bookmark resources for quick access. Bookmarked resources are shown in the dashboard.
- **Download Tracking**: Tracks user downloads and trending resources. Recent views and download counts are displayed in the dashboard.
- **Dark Theme**: Professional dark mode with smooth transitions, gradient backgrounds, and theme persistence.
- **Accessibility**: Keyboard navigation, focus indicators, ARIA labels, and high contrast support.
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
- **Bookmark Resource:** Click the bookmark icon to save resources for later. Bookmarked resources appear in your dashboard.
- **Dashboard:** Access your personalized dashboard for stats, recent activity, bookmarks, and trending resources. Admins see upload stats and pending requests.
- **Theme Toggle:** Switch between light and dark mode using the theme toggle in the header. Theme preference is saved.

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
  - `GET /api/dashboard/student` — Student dashboard data
  - `GET /api/dashboard/admin` — Admin dashboard data
  - `POST /api/resources/:id/bookmark` — Add/remove bookmark

---

## Technologies Used
- **Frontend:** Next.js, React, Tailwind CSS, Radix UI, Lucide Icons
- **Backend:** Next.js API routes, MongoDB, JWT (custom, demo only)
- **Other:** Class variance authority, Tailwind Merge, etc.

---

## Customization
- **Theme:** Easily switch between light/dark mode (see `globals.css`, Tailwind config, and theme toggle component).
- **Departments/Years/Types:** Update the lists in `app/page.js` as needed.
- **Dashboard Cards:** Customize dashboard cards and stats in `app/page.js`.
- **Animations:** Modify or add custom animations in `globals.css`.

---

## Testing
- Backend API and new dashboard features are tested and verified (see `test_result.md`).
- Frontend dark theme, dashboard, and bookmark functionality are tested and production-ready.
---

## Credits
Developed by Atul Sahu and AI.

---

## Legal Notice & Copyright

**© 2025 Atul Sahu. All rights reserved.**

This project is open source for educational and non-commercial use only. Any unauthorized copying, redistribution, commercial use, or misrepresentation of this codebase, in whole or in part, is strictly prohibited. Legal action will be taken against any individual or entity found violating these terms, regardless of the open source status. By using, forking, or referencing this repository, you agree to these terms.

For explicit permissions, licensing, or commercial inquiries, contact the project owner directly.

---

## Contact
For issues or contributions, open an issue or pull request on GitHub.
