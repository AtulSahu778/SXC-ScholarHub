'use client'

import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { BookOpen, Upload, Search, Users, FileText, GraduationCap, Download, Star, Filter, Plus, User, LogOut, Trash2, Instagram, Twitter, Github } from 'lucide-react'
import Image from 'next/image'

export default function App() {
  const [user, setUser] = useState(null)
  const [resources, setResources] = useState([])
  const [filteredResources, setFilteredResources] = useState([])
  const [loading, setLoading] = useState(false)
  const [alert, setAlert] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterDepartment, setFilterDepartment] = useState('all')
  const [filterYear, setFilterYear] = useState('all')
  const [filterType, setFilterType] = useState('all')
  const [filterSemester, setFilterSemester] = useState('all');
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [showLoginModal, setShowLoginModal] = useState(false)
  const [isLogin, setIsLogin] = useState(true)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [resourceToDelete, setResourceToDelete] = useState(null)
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [resourceToEdit, setResourceToEdit] = useState(null);

  const departments = ['Computer Science', 'Mathematics', 'Physics', 'Chemistry', 'Biology', 'English', 'History', 'Economics']
  const years = ['First Year', 'Second Year', 'Third Year']
  const resourceTypes = ['Notes', 'Previous Year Papers', 'Syllabus', 'Assignments', 'Lab Manual']
  const semesters = [
    'Semester 1', 'Semester 2', 'Semester 3', 'Semester 4',
    'Semester 5', 'Semester 6', 'Semester 7', 'Semester 8'
  ];

  const resourcesRef = useRef(null)

  useEffect(() => {
    fetchResources()
  }, [])

  useEffect(() => {
    filterResources()
  }, [resources, searchTerm, filterDepartment, filterYear, filterType, filterSemester])

  const fetchResources = async () => {
    try {
      const response = await fetch('/api/resources')
      if (response.ok) {
        const data = await response.json()
        setResources(data)
      }
    } catch (error) {
      console.error('Error fetching resources:', error)
    }
  }

  const filterResources = () => {
    let filtered = resources.filter(resource => {
      const matchesSearch = resource.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           resource.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           resource.subject.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesDepartment = filterDepartment === 'all' || resource.department === filterDepartment
      const matchesYear = filterYear === 'all' || resource.year === filterYear
      const matchesType = filterType === 'all' || resource.type === filterType
      const matchesSemester = filterSemester === 'all' || resource.semester === filterSemester
      return matchesSearch && matchesDepartment && matchesYear && matchesType && matchesSemester
    })
    setFilteredResources(filtered)
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    const formData = new FormData(e.target)
    const email = formData.get('email')
    const password = formData.get('password')

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      const data = await response.json()
      if (response.ok) {
        setUser(data.user)
        setShowLoginModal(false)
        setAlert({ type: 'success', message: 'Login successful!' })
        localStorage.setItem('token', data.token)
      } else {
        setAlert({ type: 'error', message: data.error || 'Login failed' })
      }
    } catch (error) {
      setAlert({ type: 'error', message: 'Network error. Please try again.' })
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setLoading(true)
    const formData = new FormData(e.target)
    const email = formData.get('email')
    const password = formData.get('password')
    const name = formData.get('name')
    const department = formData.get('department')
    const year = formData.get('year')

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, name, department, year })
      })

      const data = await response.json()
      if (response.ok) {
        setUser(data.user)
        setShowLoginModal(false)
        setAlert({ type: 'success', message: 'Registration successful!' })
        localStorage.setItem('token', data.token)
      } else {
        setAlert({ type: 'error', message: data.error || 'Registration failed' })
      }
    } catch (error) {
      setAlert({ type: 'error', message: 'Network error. Please try again.' })
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!user) {
      setAlert({ type: 'error', message: 'Please login to upload resources' })
      return
    }

    if (user.role !== 'admin') {
      setAlert({ type: 'error', message: 'Only administrators can upload resources' })
      return
    }

    setLoading(true)
    const formData = new FormData(e.target)
    const file = formData.get('file');
    const rawGdriveLink = formData.get('gdriveLink')?.trim();
    const gdriveLink = rawGdriveLink?.replace(/^@+/, ''); // Remove leading @

    const isAdmin = user && user.role === 'admin';
    const requiredFields = [
      formData.get('title'),
      formData.get('subject'),
      formData.get('department'),
      formData.get('year'),
      formData.get('semester'),
      formData.get('type')
    ];
    if (!isAdmin && requiredFields.some(val => !val || val === '' || val === 'all')) {
      setAlert({ type: 'error', message: 'Please fill in all required fields.' });
      setLoading(false);
      return;
    }

    const hasFile = file && file.name; // Only true if a file is actually selected

    if (!hasFile && !gdriveLink) {
      setAlert({ type: 'error', message: 'Please select a file or provide a Google Drive link' });
      setLoading(false);
      return;
    }
    if (hasFile && gdriveLink) {
      setAlert({ type: 'error', message: 'Please provide only one: file or Google Drive link' });
      setLoading(false);
      return;
    }
    if (gdriveLink) {
      if (!gdriveLink.startsWith('https://drive.google.com/')) {
        setAlert({ type: 'error', message: 'Please enter a valid Google Drive link.' })
        setLoading(false)
        return;
      }
      // Upload as link only
      try {
        const resourceData = {
          title: formData.get('title'),
          description: formData.get('description'),
          subject: formData.get('subject'),
          department: formData.get('department'),
          year: formData.get('year'),
          semester: formData.get('semester'),
          type: formData.get('type'),
          gdriveLink,
          uploadedAt: new Date().toISOString()
        }
        const token = localStorage.getItem('token')
        const response = await fetch('/api/resources', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(resourceData)
        })
        const data = await response.json()
        if (response.ok) {
          setAlert({ type: 'success', message: 'Resource uploaded successfully!' })
          setShowUploadModal(false)
          fetchResources()
          e.target.reset()
        } else {
          setAlert({ type: 'error', message: data.error || 'Upload failed' })
        }
      } catch (error) {
        setAlert({ type: 'error', message: 'Upload failed. Please try again.' })
      } finally {
        setLoading(false)
      }
      return
    }
    if (file) {
      // Convert file to base64
      const reader = new FileReader()
      reader.onload = async (ev) => {
        try {
          const resourceData = {
            title: formData.get('title'),
            description: formData.get('description'),
            subject: formData.get('subject'),
            department: formData.get('department'),
            year: formData.get('year'),
            semester: formData.get('semester'),
            type: formData.get('type'),
            fileContent: ev.target.result,
            fileName: file.name,
            fileType: file.type,
            uploadedAt: new Date().toISOString()
          }
          const token = localStorage.getItem('token')
          const response = await fetch('/api/resources', {
            method: 'POST',
            headers: { 
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(resourceData)
          })
          const data = await response.json()
          if (response.ok) {
            setAlert({ type: 'success', message: 'Resource uploaded successfully!' })
            setShowUploadModal(false)
            fetchResources()
            e.target.reset()
          } else {
            setAlert({ type: 'error', message: data.error || 'Upload failed' })
          }
        } catch (error) {
          setAlert({ type: 'error', message: 'Upload failed. Please try again.' })
        } finally {
          setLoading(false)
        }
      }
      reader.readAsDataURL(file)
    }
  }

  const handleDownload = async (resource) => {
    const token = localStorage.getItem('token')
    if (!token) {
      setAlert({ type: 'error', message: 'Please login to download files.' })
      return
    }
    try {
      const response = await fetch(`/api/resources/${resource.id}/download`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!response.ok) throw new Error('Download failed')
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = resource.fileName
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      setAlert({ type: 'error', message: 'Download failed or unauthorized.' })
    }
  }

  const handleDeleteResource = async (resource) => {
    setLoading(true)
    const token = localStorage.getItem('token')
    try {
      const response = await fetch(`/api/resources/${resource.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      if (response.ok) {
        setAlert({ type: 'success', message: 'Resource deleted successfully!' })
        fetchResources()
      } else {
        const data = await response.json()
        setAlert({ type: 'error', message: data.error || 'Delete failed' })
      }
    } catch (error) {
      setAlert({ type: 'error', message: 'Delete failed. Please try again.' })
    } finally {
      setLoading(false)
      setDeleteDialogOpen(false)
      setResourceToDelete(null)
    }
  }

  const handleEditResource = (resource) => {
    setResourceToEdit(resource);
    setEditDialogOpen(true);
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    if (!user || user.role !== 'admin' || !resourceToEdit) return;
    setLoading(true);
    const formData = new FormData(e.target);
    const updatedData = {
      title: formData.get('title'),
      description: formData.get('description'),
      subject: formData.get('subject'),
      department: formData.get('department'),
      year: formData.get('year'),
      semester: formData.get('semester'),
      type: formData.get('type'),
      gdriveLink: formData.get('gdriveLink')?.trim() || '',
    };
    // Only send fileContent if a new file is selected
    const file = formData.get('file');
    if (file && file.name) {
      const reader = new FileReader();
      reader.onload = async (ev) => {
        updatedData.fileContent = ev.target.result;
        updatedData.fileName = file.name;
        updatedData.fileType = file.type;
        await submitEdit(updatedData);
      };
      reader.readAsDataURL(file);
    } else {
      await submitEdit(updatedData);
    }
  };

  const submitEdit = async (updatedData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/resources/${resourceToEdit.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(updatedData),
      });
      const data = await response.json();
      if (response.ok) {
        setAlert({ type: 'success', message: 'Resource updated successfully!' });
        setEditDialogOpen(false);
        setResourceToEdit(null);
        fetchResources();
      } else {
        setAlert({ type: 'error', message: data.error || 'Update failed' });
      }
    } catch (error) {
      setAlert({ type: 'error', message: 'Update failed. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setUser(null)
    localStorage.removeItem('token')
    setAlert({ type: 'success', message: 'Logged out successfully' })
  }

  const handleBrowseResources = () => {
    if (resourcesRef.current) {
      resourcesRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }

  // Check for existing token on component mount
  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      // Verify token and get user info
      fetch('/api/auth/verify', {
        headers: { 'Authorization': `Bearer ${token}` }
      }).then(res => res.json()).then(data => {
        if (data.user) {
          setUser(data.user)
        }
      }).catch(() => {
        localStorage.removeItem('token')
      })
    }
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-30">
        <div className="container mx-auto px-2 sm:px-4 py-3 sm:py-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-2 sm:gap-0">
            <div className="flex items-center space-x-2">
              <Image src="/sxc-logofinal.png" alt="SXC ScholarHub Logo" width={48} height={48} className="rounded-full bg-white" />
              <div>
                <h1 className="text-xl sm:text-2xl font-bold text-gray-900">SXC ScholarHub</h1>
                <p className="text-xs sm:text-sm text-gray-600">St. Xavier's College Academic Resources</p>
              </div>
            </div>
            <div className="flex items-center space-x-2 sm:space-x-4 mt-2 sm:mt-0">
              {user ? (
                <>
                  <div className="flex items-center space-x-1 sm:space-x-2">
                    <User className="h-4 w-4" />
                    <span className="text-xs sm:text-sm font-medium truncate max-w-[80px] sm:max-w-none">{user.name}</span>
                    <Badge variant="secondary" className="text-xs">{user.role}</Badge>
                  </div>
                  <Button variant="outline" size="sm" onClick={handleLogout} className="text-xs sm:text-sm px-2 sm:px-3">
                    <LogOut className="h-4 w-4 mr-1 sm:mr-2" />
                    Logout
                  </Button>
                </>
              ) : (
                <Button onClick={() => setShowLoginModal(true)} className="text-xs sm:text-sm px-2 sm:px-3">
                  <User className="h-4 w-4 mr-1 sm:mr-2" />
                  Login
                </Button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Alert */}
      {alert && (
        <div className="container mx-auto px-2 sm:px-4 pt-3 sm:pt-4">
          <Alert className={`${alert.type === 'error' ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}> 
            <AlertDescription className={alert.type === 'error' ? 'text-red-800' : 'text-green-800'}>
              {alert.message}
            </AlertDescription>
          </Alert>
        </div>
      )}

      {/* Main Content */}
      <main className="container mx-auto px-2 sm:px-4 py-6 sm:py-8">
        {/* Hero Section */}
        <div className="text-center mb-8 sm:mb-12">
          <h2 className="text-2xl sm:text-4xl font-bold text-gray-900 mb-2 sm:mb-4">
            Your Academic Resources Hub
          </h2>
          <p className="text-base sm:text-xl text-gray-600 mb-4 sm:mb-8">
            Centralized platform for study materials, previous year papers, and academic assistance
          </p>
          <div className="flex flex-col sm:flex-row justify-center items-center gap-2 sm:space-x-4">
            {user && user.role === 'admin' && (
              <Dialog open={showUploadModal} onOpenChange={setShowUploadModal}>
                <DialogTrigger asChild>
                  <Button size="lg" className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700">
                    <Upload className="h-5 w-5 mr-2" />
                    Upload Resource
                  </Button>
                </DialogTrigger>
              </Dialog>
            )}
            <Button variant="outline" size="lg" className="w-full sm:w-auto" onClick={handleBrowseResources}>
              <BookOpen className="h-5 w-5 mr-2" />
              Browse Resources
            </Button>
          </div>
        </div>

        {/* Search and Filter Section */}
        <div className="bg-white rounded-lg shadow-sm p-3 sm:p-6 mb-6 sm:mb-8 dark:bg-[#1A1829] dark:text-[#F0F2F5]">
          <div className="grid grid-cols-1 gap-3 sm:gap-4 md:grid-cols-6">
            <div className="md:col-span-2">
              <Label htmlFor="search">Search Resources</Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400 dark:text-[#A484F0]" />
                <Input
                  id="search"
                  placeholder="Search by title, subject, or description..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 text-sm sm:text-base dark:bg-[#23203A] dark:text-[#F0F2F5] dark:placeholder-[#667085]"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="department">Department</Label>
              <Select value={filterDepartment} onValueChange={setFilterDepartment}>
                <SelectTrigger className="text-sm sm:text-base dark:bg-[#23203A] dark:text-[#F0F2F5]">
                  <SelectValue placeholder="All Departments" />
                </SelectTrigger>
                <SelectContent className="dark:bg-[#23203A] dark:text-[#F0F2F5]">
                  <SelectItem value="all">All Departments</SelectItem>
                  {departments.map(dept => (
                    <SelectItem key={dept} value={dept}>{dept}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="year">Year</Label>
              <Select value={filterYear} onValueChange={setFilterYear}>
                <SelectTrigger className="text-sm sm:text-base dark:bg-[#23203A] dark:text-[#F0F2F5]">
                  <SelectValue placeholder="All Years" />
                </SelectTrigger>
                <SelectContent className="dark:bg-[#23203A] dark:text-[#F0F2F5]">
                  <SelectItem value="all">All Years</SelectItem>
                  {years.map(year => (
                    <SelectItem key={year} value={year}>{year}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="semester">Semester</Label>
              <Select value={filterSemester} onValueChange={setFilterSemester}>
                <SelectTrigger className="text-sm sm:text-base dark:bg-[#23203A] dark:text-[#F0F2F5]">
                  <SelectValue placeholder="All Semesters" />
                </SelectTrigger>
                <SelectContent className="dark:bg-[#23203A] dark:text-[#F0F2F5]">
                  <SelectItem value="all">All Semesters</SelectItem>
                  {semesters.map(sem => (
                    <SelectItem key={sem} value={sem}>{sem}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="type">Type</Label>
              <Select value={filterType} onValueChange={setFilterType}>
                <SelectTrigger className="text-sm sm:text-base dark:bg-[#23203A] dark:text-[#F0F2F5]">
                  <SelectValue placeholder="All Types" />
                </SelectTrigger>
                <SelectContent className="dark:bg-[#23203A] dark:text-[#F0F2F5]">
                  <SelectItem value="all">All Types</SelectItem>
                  {resourceTypes.map(type => (
                    <SelectItem key={type} value={type}>{type}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        {/* Resources Grid */}
        <div ref={resourcesRef} className="grid grid-cols-1 gap-4 sm:gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredResources.map((resource) => (
            <Card key={resource.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex flex-col gap-1 sm:flex-row sm:justify-between sm:items-start">
                  <div>
                    <CardTitle className="text-base sm:text-lg">{resource.title}</CardTitle>
                    <CardDescription className="text-xs sm:text-sm">{resource.subject}</CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs sm:text-sm mt-1 sm:mt-0">{resource.type}</Badge>
                    {user && user.role === 'admin' && (
                      <>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="text-blue-600 hover:bg-blue-100 p-1"
                          title="Edit Resource"
                          onClick={() => handleEditResource(resource)}
                        >
                          <Plus className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="text-red-600 hover:bg-red-100 p-1"
                          title="Delete Resource"
                          onClick={() => { setResourceToDelete(resource); setDeleteDialogOpen(true) }}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-xs sm:text-sm text-gray-600 mb-2 sm:mb-4">{resource.description}</p>
                <div className="flex flex-wrap gap-1 sm:gap-2 mb-2 sm:mb-4">
                  <Badge variant="secondary" className="text-xs sm:text-sm">{resource.department}</Badge>
                  <Badge variant="secondary" className="text-xs sm:text-sm">{resource.year}</Badge>
                  {resource.semester && (
                    <Badge variant="secondary" className="text-xs sm:text-sm">
                      {resource.semester === 'all' ? 'All Semesters' : resource.semester}
                    </Badge>
                  )}
                </div>
                <div className="flex flex-col sm:flex-row justify-between items-center gap-2 sm:gap-0">
                  <div className="text-xs text-gray-500">
                    {new Date(resource.uploadedAt).toLocaleDateString()}
                  </div>
                  {resource.gdriveLink ? (
                    <a
                      href={resource.gdriveLink}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="bg-blue-600 hover:bg-blue-700 w-full sm:w-auto text-xs sm:text-sm px-3 py-2 rounded text-white flex items-center justify-center"
                    >
                      <Download className="h-4 w-4 mr-1 sm:mr-2" />
                      View on Google Drive
                    </a>
                  ) : (
                    <Button
                      size="sm"
                      onClick={() => handleDownload(resource)}
                      className="bg-green-600 hover:bg-green-700 w-full sm:w-auto text-xs sm:text-sm"
                    >
                      <Download className="h-4 w-4 mr-1 sm:mr-2" />
                      Download
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredResources.length === 0 && (
          <div className="text-center py-8 sm:py-12">
            <FileText className="h-12 w-12 sm:h-16 sm:w-16 text-gray-400 mx-auto mb-2 sm:mb-4" />
            <h3 className="text-base sm:text-lg font-medium text-gray-900 mb-1 sm:mb-2">No resources found</h3>
            <p className="text-xs sm:text-base text-gray-500">Try adjusting your search criteria or upload new resources.</p>
          </div>
        )}
      </main>

      {/* Upload Modal */}
      <Dialog open={showUploadModal} onOpenChange={setShowUploadModal}>
        <DialogContent className="w-[95vw] max-w-[95vw] sm:max-w-[500px] p-2 sm:p-6">
          <DialogHeader>
            <DialogTitle className="text-base sm:text-lg">Upload Academic Resource</DialogTitle>
            <DialogDescription className="text-xs sm:text-sm">
              Share your study materials with fellow students at SXC
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleUpload} className="space-y-3 sm:space-y-4">
            <div>
              <Label htmlFor="title">Title</Label>
              <Input id="title" name="title" placeholder="e.g., Data Structures Notes" className="text-sm sm:text-base" />
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea id="description" name="description" placeholder="Brief description of the resource" className="text-sm sm:text-base" />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
              <div>
                <Label htmlFor="subject">Subject</Label>
                <Input id="subject" name="subject" placeholder="e.g., Computer Science" className="text-sm sm:text-base" />
              </div>
              <div>
                <Label htmlFor="department">Department</Label>
                <Select name="department">
                  <SelectTrigger className="text-sm sm:text-base">
                    <SelectValue placeholder="Select Department" />
                  </SelectTrigger>
                  <SelectContent>
                    {departments.map(dept => (
                      <SelectItem key={dept} value={dept}>{dept}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
              <div>
                <Label htmlFor="year">Year</Label>
                <Select name="year">
                  <SelectTrigger className="text-sm sm:text-base">
                    <SelectValue placeholder="Select Year" />
                  </SelectTrigger>
                  <SelectContent>
                    {years.map(year => (
                      <SelectItem key={year} value={year}>{year}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="semester">Semester</Label>
                <Select name="semester">
                  <SelectTrigger className="text-sm sm:text-base dark:bg-[#23203A] dark:text-[#F0F2F5]">
                    <SelectValue placeholder="Select Semester" />
                  </SelectTrigger>
                  <SelectContent className="dark:bg-[#23203A] dark:text-[#F0F2F5]">
                    <SelectItem value="all">All Semesters</SelectItem>
                    {semesters.map(sem => (
                      <SelectItem key={sem} value={sem}>{sem}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label htmlFor="type">Type</Label>
              <Select name="type">
                <SelectTrigger className="text-sm sm:text-base">
                  <SelectValue placeholder="Select Type" />
                </SelectTrigger>
                <SelectContent>
                  {resourceTypes.map(type => (
                    <SelectItem key={type} value={type}>{type}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="file">File</Label>
              <Input id="file" name="file" type="file" accept=".pdf,.doc,.docx,.ppt,.pptx" className="text-sm sm:text-base" />
              <div className="text-xs text-gray-500 mt-1">Or provide a Google Drive link below instead of uploading a file.</div>
              <Input id="gdriveLink" name="gdriveLink" type="url" placeholder="https://drive.google.com/..." className="text-sm sm:text-base mt-2" />
            </div>
            <div className="flex flex-col sm:flex-row justify-end gap-2">
              <Button type="button" variant="outline" onClick={() => setShowUploadModal(false)} className="w-full sm:w-auto text-xs sm:text-sm">
                Cancel
              </Button>
              <Button type="submit" disabled={loading} className="w-full sm:w-auto text-xs sm:text-sm">
                {loading ? 'Uploading...' : 'Upload Resource'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Login/Register Modal */}
      <Dialog open={showLoginModal} onOpenChange={setShowLoginModal}>
        <DialogContent className="w-[95vw] max-w-[95vw] sm:max-w-[400px] p-2 sm:p-6">
          <DialogHeader>
            <DialogTitle className="text-base sm:text-lg">{isLogin ? 'Login' : 'Register'} to SXC ScholarHub</DialogTitle>
            <DialogDescription className="text-xs sm:text-sm">
              {isLogin ? 'Sign in to your account' : 'Create a new account'}
            </DialogDescription>
          </DialogHeader>
          <Tabs value={isLogin ? 'login' : 'register'} onValueChange={(value) => setIsLogin(value === 'login')}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="login" className="text-xs sm:text-sm">Login</TabsTrigger>
              <TabsTrigger value="register" className="text-xs sm:text-sm">Register</TabsTrigger>
            </TabsList>
            <TabsContent value="login">
              <form onSubmit={handleLogin} className="space-y-3 sm:space-y-4">
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" name="email" type="email" required className="text-sm sm:text-base" />
                </div>
                <div>
                  <Label htmlFor="password">Password</Label>
                  <Input id="password" name="password" type="password" required className="text-sm sm:text-base" />
                </div>
                <Button type="submit" className="w-full text-xs sm:text-sm" disabled={loading}>
                  {loading ? 'Logging in...' : 'Login'}
                </Button>
              </form>
            </TabsContent>
            <TabsContent value="register">
              <form onSubmit={handleRegister} className="space-y-3 sm:space-y-4">
                <div>
                  <Label htmlFor="name">Full Name</Label>
                  <Input id="name" name="name" required className="text-sm sm:text-base" />
                </div>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" name="email" type="email" required className="text-sm sm:text-base" />
                </div>
                <div>
                  <Label htmlFor="password">Password</Label>
                  <Input id="password" name="password" type="password" required className="text-sm sm:text-base" />
                </div>
                <div>
                  <Label htmlFor="department">Department</Label>
                  <Select name="department" required>
                    <SelectTrigger className="text-sm sm:text-base">
                      <SelectValue placeholder="Select Department" />
                    </SelectTrigger>
                    <SelectContent>
                      {departments.map(dept => (
                        <SelectItem key={dept} value={dept}>{dept}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="year">Year</Label>
                  <Select name="year" required>
                    <SelectTrigger className="text-sm sm:text-base">
                      <SelectValue placeholder="Select Year" />
                    </SelectTrigger>
                    <SelectContent>
                      {years.map(year => (
                        <SelectItem key={year} value={year}>{year}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <Button type="submit" className="w-full text-xs sm:text-sm" disabled={loading}>
                  {loading ? 'Creating Account...' : 'Create Account'}
                </Button>
              </form>
            </TabsContent>
          </Tabs>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent className="w-[90vw] max-w-[350px]">
          <DialogHeader>
            <DialogTitle className="text-base">Confirm Delete</DialogTitle>
            <DialogDescription className="text-xs">
              Are you sure you want to delete <span className="font-semibold">{resourceToDelete?.title}</span>? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end gap-2 mt-4">
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)} className="text-xs">Cancel</Button>
            <Button variant="destructive" onClick={() => handleDeleteResource(resourceToDelete)} disabled={loading} className="text-xs">
              {loading ? 'Deleting...' : 'Delete'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Edit Resource Modal */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="w-[95vw] max-w-[95vw] sm:max-w-[500px] p-2 sm:p-6 dark:bg-[#1A1829] dark:text-[#F0F2F5]">
          <DialogHeader>
            <DialogTitle className="text-base sm:text-lg">Edit Academic Resource</DialogTitle>
            <DialogDescription className="text-xs sm:text-sm">
              Update the details of this resource
            </DialogDescription>
          </DialogHeader>
          {resourceToEdit && (
            <form onSubmit={handleEditSubmit} className="space-y-3 sm:space-y-4">
              <div>
                <Label htmlFor="edit-title">Title</Label>
                <Input id="edit-title" name="title" defaultValue={resourceToEdit.title} required className="text-sm sm:text-base dark:bg-[#23203A] dark:text-[#F0F2F5]" />
              </div>
              <div>
                <Label htmlFor="edit-description">Description</Label>
                <Textarea id="edit-description" name="description" defaultValue={resourceToEdit.description} className="text-sm sm:text-base dark:bg-[#23203A] dark:text-[#F0F2F5]" />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div>
                  <Label htmlFor="edit-subject">Subject</Label>
                  <Input id="edit-subject" name="subject" defaultValue={resourceToEdit.subject} required className="text-sm sm:text-base dark:bg-[#23203A] dark:text-[#F0F2F5]" />
                </div>
                <div>
                  <Label htmlFor="edit-department">Department</Label>
                  <Select name="department" defaultValue={resourceToEdit.department} required>
                    <SelectTrigger className="text-sm sm:text-base dark:bg-[#23203A] dark:text-[#F0F2F5]">
                      <SelectValue placeholder="Select Department" />
                    </SelectTrigger>
                    <SelectContent className="dark:bg-[#23203A] dark:text-[#F0F2F5]">
                      {departments.map(dept => (
                        <SelectItem key={dept} value={dept}>{dept}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div>
                  <Label htmlFor="edit-year">Year</Label>
                  <Select name="year" defaultValue={resourceToEdit.year} required>
                    <SelectTrigger className="text-sm sm:text-base dark:bg-[#23203A] dark:text-[#F0F2F5]">
                      <SelectValue placeholder="Select Year" />
                    </SelectTrigger>
                    <SelectContent className="dark:bg-[#23203A] dark:text-[#F0F2F5]">
                      {years.map(year => (
                        <SelectItem key={year} value={year}>{year}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="edit-semester">Semester</Label>
                  <Select name="semester" defaultValue={resourceToEdit.semester} required>
                    <SelectTrigger className="text-sm sm:text-base dark:bg-[#23203A] dark:text-[#F0F2F5]">
                      <SelectValue placeholder="Select Semester" />
                    </SelectTrigger>
                    <SelectContent className="dark:bg-[#23203A] dark:text-[#F0F2F5]">
                      <SelectItem value="all">All Semesters</SelectItem>
                      {semesters.map(sem => (
                        <SelectItem key={sem} value={sem}>{sem}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div>
                  <Label htmlFor="edit-type">Type</Label>
                  <Select name="type" defaultValue={resourceToEdit.type} required>
                    <SelectTrigger className="text-sm sm:text-base dark:bg-[#23203A] dark:text-[#F0F2F5]">
                      <SelectValue placeholder="Select Type" />
                    </SelectTrigger>
                    <SelectContent className="dark:bg-[#23203A] dark:text-[#F0F2F5]">
                      {resourceTypes.map(type => (
                        <SelectItem key={type} value={type}>{type}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="edit-gdriveLink">Google Drive Link</Label>
                  <Input id="edit-gdriveLink" name="gdriveLink" type="url" defaultValue={resourceToEdit.gdriveLink} placeholder="https://drive.google.com/..." className="text-sm sm:text-base dark:bg-[#23203A] dark:text-[#F0F2F5]" />
                </div>
              </div>
              <div>
                <Label htmlFor="edit-file">Replace File (optional)</Label>
                <Input id="edit-file" name="file" type="file" accept=".pdf,.doc,.docx,.ppt,.pptx" className="text-sm sm:text-base dark:bg-[#23203A] dark:text-[#F0F2F5]" />
                <div className="text-xs text-gray-500 mt-1 dark:text-[#667085]">Leave blank to keep the current file.</div>
              </div>
              <div className="flex flex-col sm:flex-row justify-end gap-2">
                <Button type="button" variant="outline" onClick={() => setEditDialogOpen(false)} className="w-full sm:w-auto text-xs sm:text-sm">
                  Cancel
                </Button>
                <Button type="submit" disabled={loading} className="w-full sm:w-auto text-xs sm:text-sm bg-gradient-to-r from-[#7F56D9] to-[#A484F0] text-[#F0F2F5]">
                  {loading ? 'Saving...' : 'Save Changes'}
                </Button>
              </div>
            </form>
          )}
        </DialogContent>
      </Dialog>

      {/* Footer */}
      <footer className="w-full border-t bg-white mt-8 py-4">
        <div className="container mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-gray-500">
          <div>Built by <span className="font-semibold text-gray-700">Atul Sahu</span></div>
          <div className="flex gap-4 items-center">
            <a href="https://instagram.com/ofc_atul" target="_blank" rel="noopener noreferrer" title="Instagram" className="hover:text-blue-600 flex items-center gap-1">
              <Instagram className="h-4 w-4" /> ofc_atul
            </a>
            <a href="https://twitter.com/Ofc-atul" target="_blank" rel="noopener noreferrer" title="Twitter" className="hover:text-blue-600 flex items-center gap-1">
              <Twitter className="h-4 w-4" /> Ofc-atul
            </a>
            <a href="https://github.com/AtulSahu778" target="_blank" rel="noopener noreferrer" title="GitHub" className="hover:text-blue-600 flex items-center gap-1">
              <Github className="h-4 w-4" /> AtulSahu778
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}