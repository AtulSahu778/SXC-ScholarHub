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
import { ThemeToggle } from '@/components/ui/theme-toggle'
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { BookOpen, Upload, Search, Users, FileText, GraduationCap, Download, Star, Filter, Plus, User, LogOut, Trash2, Instagram, Twitter, Github, Palette, BarChart3, TrendingUp, Bookmark, BookmarkCheck, Menu, X } from 'lucide-react'
import Image from 'next/image'
import { useRouter } from 'next/navigation';

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
  const [showDashboard, setShowDashboard] = useState(false)
  const [dashboardData, setDashboardData] = useState(null)
  const [bookmarkedResources, setBookmarkedResources] = useState(new Set())
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const departments = ['Computer Science', 'Mathematics', 'Physics', 'Chemistry', 'Biology', 'English', 'History', 'Economics']
  const years = ['First Year', 'Second Year', 'Third Year']
  const resourceTypes = ['Notes', 'Previous Year Papers', 'Syllabus', 'Assignments', 'Lab Manual']
  const semesters = [
    'Semester 1', 'Semester 2', 'Semester 3', 'Semester 4',
    'Semester 5', 'Semester 6', 'Semester 7', 'Semester 8'
  ];

  const resourcesRef = useRef(null)
  const router = useRouter();

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
        
        // Update bookmarked resources set if user is logged inn
        if (user) {
          fetchDashboardData()
        }
      }
    } catch (error) {
      console.error('Error fetching resources:', error)
    }
  }

  const fetchDashboardData = async () => {
    if (!user) return
    
    const token = localStorage.getItem('token')
    if (!token) return

    try {
      const endpoint = user.role === 'admin' ? '/api/dashboard/admin' : '/api/dashboard/student'
      const response = await fetch(endpoint, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        const data = await response.json()
        setDashboardData(data)
        
        // Update bookmarked resources set for students
        if (user.role === 'student' && data.bookmarkedResources) {
          const bookmarkedIds = new Set(data.bookmarkedResources.map(r => r.id))
          setBookmarkedResources(bookmarkedIds)
        }
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    }
  }

  const handleBookmark = async (resourceId) => {
    const token = localStorage.getItem('token')
    if (!token) {
      setAlert({ type: 'error', message: 'Please login to bookmark resources.' })
      return
    }

    try {
      const response = await fetch(`/api/resources/${resourceId}/bookmark`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        const data = await response.json()
        
        // Update bookmarked resources set
        const newBookmarks = new Set(bookmarkedResources)
        if (data.isBookmarked) {
          newBookmarks.add(resourceId)
        } else {
          newBookmarks.delete(resourceId)
        }
        setBookmarkedResources(newBookmarks)
        
        // Refresh dashboard data
        fetchDashboardData()
        
        setAlert({ type: 'success', message: data.message })
      } else {
        const errorData = await response.json()
        setAlert({ type: 'error', message: errorData.error || 'Bookmark failed' })
      }
    } catch (error) {
      setAlert({ type: 'error', message: 'Bookmark failed. Please try again.' })
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
        // Fetch dashboard data after login
        setTimeout(() => fetchDashboardData(), 100)
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
        // Fetch dashboard data after registration
        setTimeout(() => fetchDashboardData(), 100)
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
    setMobileMenuOpen(false)
  }

  const handleBrowseResources = () => {
    if (resourcesRef.current) {
      resourcesRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
    setMobileMenuOpen(false)
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
          // Fetch dashboard data after user verification
          setTimeout(() => fetchDashboardData(), 100)
        }
      }).catch(() => {
        localStorage.removeItem('token')
      })
    }
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-background dark:to-card transition-colors duration-300">
      {/* Enhanced Responsive Header */}
      <header className="bg-white/80 dark:bg-card/80 backdrop-blur-md shadow-sm border-b border-border sticky top-0 z-30 transition-all duration-300">
        <div className="container mx-auto px-3 sm:px-4 lg:px-6 xl:px-8 py-3 lg:py-4">
          <div className="flex items-center justify-between">
            {/* Logo and Title - Responsive */}
            <div className="flex items-center space-x-2 lg:space-x-3">
              <div className="relative">
                <Image 
                  src="/sxc-logofinal.png" 
                  alt="SXC ScholarHub Logo" 
                  width={40} 
                  height={40}
                  className="w-8 h-8 sm:w-10 sm:h-10 lg:w-12 lg:h-12 rounded-full bg-white dark:bg-background shadow-lg transition-shadow duration-300" 
                />
                <div className="absolute -top-0.5 -right-0.5 w-3 h-3 lg:w-4 lg:h-4 bg-gradient-to-r from-primary to-purple-500 rounded-full animate-pulse"></div>
              </div>
              <div className="hidden xs:block">
                <h1 className="text-lg sm:text-xl lg:text-2xl xl:text-3xl font-bold text-gray-900 dark:text-foreground gradient-text">
                  SXC ScholarHub
                </h1>
                <p className="text-xs sm:text-sm lg:text-base text-gray-600 dark:text-muted-foreground">
                  St. Xavier's College Academic Resources
                </p>
              </div>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-2 lg:space-x-4">
              <ThemeToggle />
              {user ? (
                <>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => setShowDashboard(!showDashboard)}
                    className="text-sm lg:text-base px-3 lg:px-4 hover:bg-primary/10 transition-all duration-200"
                  >
                    <BarChart3 className="h-4 w-4 lg:h-5 lg:w-5 mr-2" />
                    Dashboard
                  </Button>
                  <div className="flex items-center space-x-2 lg:space-x-3 px-3 py-1.5 rounded-lg bg-accent/50">
                    <User className="h-4 w-4 lg:h-5 lg:w-5" />
                    <div className="flex flex-col">
                      <span className="text-sm lg:text-base font-medium leading-none">{user.name}</span>
                      <Badge variant="secondary" className="text-xs mt-0.5 w-fit">{user.role}</Badge>
                    </div>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={handleLogout} 
                    className="text-sm lg:text-base px-3 lg:px-4 hover:bg-destructive hover:text-destructive-foreground transition-all duration-200"
                  >
                    <LogOut className="h-4 w-4 lg:h-5 lg:w-5 mr-2" />
                    Logout
                  </Button>
                </>
              ) : (
                <Button 
                  onClick={() => setShowLoginModal(true)} 
                  className="text-sm lg:text-base px-4 lg:px-6 bg-gradient-to-r from-primary to-purple-500 hover:from-purple-600 hover:to-primary transition-all duration-200"
                >
                  <User className="h-4 w-4 lg:h-5 lg:w-5 mr-2" />
                  Login
                </Button>
              )}
            </div>

            {/* Mobile Menu Button */}
            <div className="flex md:hidden items-center space-x-2">
              <ThemeToggle />
              <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
                <SheetTrigger asChild>
                  <Button variant="outline" size="sm" className="p-2">
                    <Menu className="h-5 w-5" />
                  </Button>
                </SheetTrigger>
                <SheetContent side="right" className="w-[300px] sm:w-[400px]">
                  <SheetHeader>
                    <SheetTitle className="flex items-center space-x-2">
                      <Image 
                        src="/sxc-logofinal.png" 
                        alt="SXC ScholarHub Logo" 
                        width={32} 
                        height={32}
                        className="rounded-full" 
                      />
                      <span>SXC ScholarHub</span>
                    </SheetTitle>
                    <SheetDescription>
                      Academic Resources Platform
                    </SheetDescription>
                  </SheetHeader>
                  <div className="mt-6 flex flex-col space-y-4">
                    {user ? (
                      <>
                        <div className="flex items-center space-x-3 p-4 rounded-lg bg-accent/50">
                          <User className="h-8 w-8" />
                          <div>
                            <div className="font-medium">{user.name}</div>
                            <Badge variant="secondary" className="text-xs">{user.role}</Badge>
                          </div>
                        </div>
                        <Button 
                          variant="outline" 
                          onClick={() => {
                            setShowDashboard(!showDashboard)
                            setMobileMenuOpen(false)
                          }}
                          className="justify-start h-12"
                        >
                          <BarChart3 className="h-5 w-5 mr-3" />
                          Dashboard
                        </Button>
                        <Button 
                          variant="outline" 
                          onClick={handleBrowseResources}
                          className="justify-start h-12"
                        >
                          <BookOpen className="h-5 w-5 mr-3" />
                          Browse Resources
                        </Button>
                        {user.role === 'admin' && (
                          <Button 
                            variant="outline" 
                            onClick={() => {
                              setShowUploadModal(true)
                              setMobileMenuOpen(false)
                            }}
                            className="justify-start h-12"
                          >
                            <Upload className="h-5 w-5 mr-3" />
                            Upload Resource
                          </Button>
                        )}
                        <Button 
                          variant="outline" 
                          onClick={handleLogout}
                          className="justify-start h-12 hover:bg-destructive hover:text-destructive-foreground"
                        >
                          <LogOut className="h-5 w-5 mr-3" />
                          Logout
                        </Button>
                      </>
                    ) : (
                      <Button 
                        onClick={() => {
                          setShowLoginModal(true)
                          setMobileMenuOpen(false)
                        }}
                        className="h-12 bg-gradient-to-r from-primary to-purple-500"
                      >
                        <User className="h-5 w-5 mr-3" />
                        Login / Register
                      </Button>
                    )}
                  </div>
                </SheetContent>
              </Sheet>
            </div>
          </div>
        </div>
      </header>

      {/* Enhanced Alert - Responsive */}
      {alert && (
        <div className="container mx-auto px-3 sm:px-4 lg:px-6 xl:px-8 pt-3 sm:pt-4 animate-slide-up">
          <Alert className={`${
            alert.type === 'error' 
              ? 'bg-red-50/80 dark:bg-red-950/20 border-red-200 dark:border-red-800 backdrop-blur-sm' 
              : 'bg-green-50/80 dark:bg-green-950/20 border-green-200 dark:border-green-800 backdrop-blur-sm'
          } transition-all duration-300`}> 
            <AlertDescription className={`text-sm lg:text-base ${
              alert.type === 'error' 
                ? 'text-red-800 dark:text-red-400' 
                : 'text-green-800 dark:text-green-400'
            }`}>
              {alert.message}
            </AlertDescription>
          </Alert>
        </div>
      )}

      {/* Enhanced Main Content - Ultra Responsive */}
      <main className="container mx-auto px-3 sm:px-4 lg:px-6 xl:px-8 py-6 lg:py-8 xl:py-12 max-w-8xl">
        {/* Enhanced Hero Section - Fully Responsive */}
        <div className="text-center mb-8 lg:mb-12 xl:mb-16 animate-fade-in">
          <div className="relative mb-4 lg:mb-6">
            <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl 2xl:text-7xl font-bold text-gray-900 dark:text-foreground mb-2 lg:mb-4 relative leading-tight">
              Your Academic Resources Hub
              <div className="absolute -inset-1 bg-gradient-to-r from-primary/20 to-purple-500/20 blur-2xl -z-10 animate-pulse"></div>
            </h2>
          </div>
          <p className="text-base sm:text-lg md:text-xl lg:text-2xl xl:text-3xl text-gray-600 dark:text-muted-foreground mb-6 lg:mb-8 xl:mb-12 max-w-2xl lg:max-w-4xl xl:max-w-6xl mx-auto leading-relaxed">
            Centralized platform for study materials, previous year papers, and academic assistance
          </p>
          <div className="flex flex-col sm:flex-row justify-center items-center gap-3 sm:gap-4 lg:gap-6">
            {user && user.role === 'admin' && (
              <Dialog open={showUploadModal} onOpenChange={setShowUploadModal}>
                <DialogTrigger asChild>
                  <Button 
                    size="lg" 
                    className="w-full sm:w-auto text-sm sm:text-base lg:text-lg px-6 lg:px-8 py-3 lg:py-4 bg-gradient-to-r from-primary to-purple-500 hover:from-purple-600 hover:to-primary text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
                  >
                    <Upload className="h-5 w-5 lg:h-6 lg:w-6 mr-2 lg:mr-3" />
                    Upload Resource
                  </Button>
                </DialogTrigger>
              </Dialog>
            )}
            <Button 
              variant="outline" 
              size="lg" 
              className="w-full sm:w-auto text-sm sm:text-base lg:text-lg px-6 lg:px-8 py-3 lg:py-4 border-primary/50 hover:bg-primary/10 dark:hover:bg-primary/10 transition-all duration-300 transform hover:scale-105" 
              onClick={handleBrowseResources}
            >
              <BookOpen className="h-5 w-5 lg:h-6 lg:w-6 mr-2 lg:mr-3" />
              Browse Resources
            </Button>
          </div>
        </div>

        {/* Smart Academic Dashboard */}
        {user && showDashboard && dashboardData && (
          <div className="mb-8 sm:mb-12 animate-fade-in">
            <h3 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-foreground mb-4 sm:mb-6">
              {user.role === 'admin' ? 'Admin Dashboard' : 'Student Dashboard'}
            </h3>
            
            {user.role === 'student' ? (
              <div className="grid grid-cols-1 gap-4 sm:gap-6 md:grid-cols-2 lg:grid-cols-4">
                {/* Total Downloads Card */}
                <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-800 hover:shadow-lg transition-all duration-300">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-blue-800 dark:text-blue-300">Total Downloads</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center space-x-2">
                      <Download className="h-8 w-8 text-blue-600 dark:text-blue-400" />
                      <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">
                        {dashboardData.totalDownloads}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Recent Resources Card */}
                <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-800 hover:shadow-lg transition-all duration-300">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-green-800 dark:text-green-300">Recent Resources</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center space-x-2">
                      <FileText className="h-8 w-8 text-green-600 dark:text-green-400" />
                      <div className="text-2xl font-bold text-green-900 dark:text-green-100">
                        {dashboardData.recentResources?.length || 0}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Bookmarked Resources Card */}
                <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20 border-yellow-200 dark:border-yellow-800 hover:shadow-lg transition-all duration-300">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-yellow-800 dark:text-yellow-300">Bookmarked</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center space-x-2">
                      <BookmarkCheck className="h-8 w-8 text-yellow-600 dark:text-yellow-400" />
                      <div className="text-2xl font-bold text-yellow-900 dark:text-yellow-100">
                        {dashboardData.bookmarkedResources?.length || 0}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Trending Resources Card */}
                <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-purple-200 dark:border-purple-800 hover:shadow-lg transition-all duration-300">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-purple-800 dark:text-purple-300">Trending</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="h-8 w-8 text-purple-600 dark:text-purple-400" />
                      <div className="text-2xl font-bold text-purple-900 dark:text-purple-100">
                        {dashboardData.trendingResources?.length || 0}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4 sm:gap-6 md:grid-cols-3">
                {/* Total Uploads Card */}
                <Card className="bg-gradient-to-br from-indigo-50 to-indigo-100 dark:from-indigo-900/20 dark:to-indigo-800/20 border-indigo-200 dark:border-indigo-800 hover:shadow-lg transition-all duration-300">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-indigo-800 dark:text-indigo-300">Total Uploads</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center space-x-2">
                      <Upload className="h-8 w-8 text-indigo-600 dark:text-indigo-400" />
                      <div className="text-2xl font-bold text-indigo-900 dark:text-indigo-100">
                        {dashboardData.totalUploads}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Recent Uploads Card */}
                <Card className="bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-900/20 dark:to-emerald-800/20 border-emerald-200 dark:border-emerald-800 hover:shadow-lg transition-all duration-300">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-emerald-800 dark:text-emerald-300">Recent Uploads</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center space-x-2">
                      <FileText className="h-8 w-8 text-emerald-600 dark:text-emerald-400" />
                      <div className="text-2xl font-bold text-emerald-900 dark:text-emerald-100">
                        {dashboardData.recentUploads?.length || 0}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Pending Requests Card */}
                <Card className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 border-orange-200 dark:border-orange-800 hover:shadow-lg transition-all duration-300">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-orange-800 dark:text-orange-300">Pending Requests</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center space-x-2">
                      <Users className="h-8 w-8 text-orange-600 dark:text-orange-400" />
                      <div className="text-2xl font-bold text-orange-900 dark:text-orange-100">
                        {dashboardData.pendingRequests?.length || 0}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Detailed Lists */}
            {user.role === 'student' && (
              <div className="grid grid-cols-1 gap-4 sm:gap-6 md:grid-cols-2 mt-6">
                {/* Recent Resources List */}
                {dashboardData.recentResources && dashboardData.recentResources.length > 0 && (
                  <Card className="bg-card/80 dark:bg-card/80 backdrop-blur-md border-border">
                    <CardHeader>
                      <CardTitle className="text-base sm:text-lg flex items-center">
                        <FileText className="h-5 w-5 mr-2" />
                        Recently Accessed
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {dashboardData.recentResources.slice(0, 5).map((resource) => (
                          <div key={resource.id} className="flex justify-between items-center p-2 rounded hover:bg-accent/50 transition-colors">
                            <div className="flex-1 min-w-0">
                              <div className="text-sm font-medium text-foreground truncate">{resource.title}</div>
                              <div className="text-xs text-muted-foreground">{resource.department} • {resource.type}</div>
                            </div>
                            <Badge variant="outline" className="text-xs ml-2">{resource.year}</Badge>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Bookmarked Resources List */}
                {dashboardData.bookmarkedResources && dashboardData.bookmarkedResources.length > 0 && (
                  <Card className="bg-card/80 dark:bg-card/80 backdrop-blur-md border-border">
                    <CardHeader>
                      <CardTitle className="text-base sm:text-lg flex items-center">
                        <BookmarkCheck className="h-5 w-5 mr-2" />
                        Bookmarked Resources
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {dashboardData.bookmarkedResources.slice(0, 5).map((resource) => (
                          <div key={resource.id} className="flex justify-between items-center p-2 rounded hover:bg-accent/50 transition-colors">
                            <div className="flex-1 min-w-0">
                              <div className="text-sm font-medium text-foreground truncate">{resource.title}</div>
                              <div className="text-xs text-muted-foreground">{resource.department} • {resource.type}</div>
                            </div>
                            <Badge variant="outline" className="text-xs ml-2">{resource.year}</Badge>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Trending Resources List */}
                {dashboardData.trendingResources && dashboardData.trendingResources.length > 0 && (
                  <Card className="bg-card/80 dark:bg-card/80 backdrop-blur-md border-border md:col-span-2">
                    <CardHeader>
                      <CardTitle className="text-base sm:text-lg flex items-center">
                        <TrendingUp className="h-5 w-5 mr-2" />
                        Trending Resources
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {dashboardData.trendingResources.map((resource) => (
                          <div key={resource.id} className="flex justify-between items-center p-2 rounded hover:bg-accent/50 transition-colors">
                            <div className="flex-1 min-w-0">
                              <div className="text-sm font-medium text-foreground truncate">{resource.title}</div>
                              <div className="text-xs text-muted-foreground">{resource.department} • {resource.type}</div>
                            </div>
                            <div className="flex items-center space-x-2 ml-2">
                              <Badge variant="outline" className="text-xs">{resource.downloadCount || 0} downloads</Badge>
                              <Badge variant="outline" className="text-xs">{resource.year}</Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}

            {/* Admin Lists */}
            {user.role === 'admin' && dashboardData.recentUploads && dashboardData.recentUploads.length > 0 && (
              <Card className="bg-card/80 dark:bg-card/80 backdrop-blur-md border-border mt-6">
                <CardHeader>
                  <CardTitle className="text-base sm:text-lg flex items-center">
                    <Upload className="h-5 w-5 mr-2" />
                    Recent Uploads
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {dashboardData.recentUploads.map((resource) => (
                      <div key={resource.id} className="flex justify-between items-center p-2 rounded hover:bg-accent/50 transition-colors">
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium text-foreground truncate">{resource.title}</div>
                          <div className="text-xs text-muted-foreground">{resource.department} • {resource.type}</div>
                        </div>
                        <div className="flex items-center space-x-2 ml-2">
                          <Badge variant="outline" className="text-xs">{new Date(resource.uploadedAt).toLocaleDateString()}</Badge>
                          <Badge variant="outline" className="text-xs">{resource.year}</Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Enhanced Search and Filter Section */}
        <div className="bg-white/80 dark:bg-card/80 backdrop-blur-md rounded-xl shadow-sm border border-border p-3 sm:p-6 mb-6 sm:mb-8 animate-scale-in">
          <div className="grid grid-cols-1 gap-3 sm:gap-4 md:grid-cols-6">
            <div className="md:col-span-2">
              <Label htmlFor="search" className="text-sm font-medium text-foreground">Search Resources</Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search"
                  placeholder="Search by title, subject, or description..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 text-sm sm:text-base bg-background/50 dark:bg-background/50 border-border focus:border-primary transition-all duration-200"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="department" className="text-sm font-medium text-foreground">Department</Label>
              <Select value={filterDepartment} onValueChange={setFilterDepartment}>
                <SelectTrigger className="text-sm sm:text-base bg-background/50 dark:bg-background/50 border-border focus:border-primary">
                  <SelectValue placeholder="All Departments" />
                </SelectTrigger>
                <SelectContent className="bg-popover/95 dark:bg-popover/95 backdrop-blur-md border-border">
                  <SelectItem value="all">All Departments</SelectItem>
                  {departments.map(dept => (
                    <SelectItem key={dept} value={dept}>{dept}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="year" className="text-sm font-medium text-foreground">Year</Label>
              <Select value={filterYear} onValueChange={setFilterYear}>
                <SelectTrigger className="text-sm sm:text-base bg-background/50 dark:bg-background/50 border-border focus:border-primary">
                  <SelectValue placeholder="All Years" />
                </SelectTrigger>
                <SelectContent className="bg-popover/95 dark:bg-popover/95 backdrop-blur-md border-border">
                  <SelectItem value="all">All Years</SelectItem>
                  {years.map(year => (
                    <SelectItem key={year} value={year}>{year}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="semester" className="text-sm font-medium text-foreground">Semester</Label>
              <Select value={filterSemester} onValueChange={setFilterSemester}>
                <SelectTrigger className="text-sm sm:text-base bg-background/50 dark:bg-background/50 border-border focus:border-primary">
                  <SelectValue placeholder="All Semesters" />
                </SelectTrigger>
                <SelectContent className="bg-popover/95 dark:bg-popover/95 backdrop-blur-md border-border">
                  <SelectItem value="all">All Semesters</SelectItem>
                  {semesters.map(sem => (
                    <SelectItem key={sem} value={sem}>{sem}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="type" className="text-sm font-medium text-foreground">Type</Label>
              <Select value={filterType} onValueChange={setFilterType}>
                <SelectTrigger className="text-sm sm:text-base bg-background/50 dark:bg-background/50 border-border focus:border-primary">
                  <SelectValue placeholder="All Types" />
                </SelectTrigger>
                <SelectContent className="bg-popover/95 dark:bg-popover/95 backdrop-blur-md border-border">
                  <SelectItem value="all">All Types</SelectItem>
                  {resourceTypes.map(type => (
                    <SelectItem key={type} value={type}>{type}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        {/* Enhanced Resources Grid */}
        <div ref={resourcesRef} className="grid grid-cols-1 gap-4 sm:gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredResources.map((resource) => (
            <Card 
              key={resource.id} 
              className="hover:shadow-lg dark:hover:shadow-2xl dark:hover:shadow-primary/10 transition-all duration-300 transform hover:scale-[1.02] bg-card/80 dark:bg-card/80 backdrop-blur-md border-border hover:border-primary/50 group"
            >
              <CardHeader>
                <div className="flex flex-col gap-1 sm:flex-row sm:justify-between sm:items-start">
                  <div>
                    <CardTitle className="text-base sm:text-lg text-card-foreground group-hover:text-primary transition-colors duration-200">
                      {resource.title}
                    </CardTitle>
                    <CardDescription className="text-xs sm:text-sm text-muted-foreground">
                      {resource.subject}
                    </CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge 
                      variant="outline" 
                      className="text-xs sm:text-sm mt-1 sm:mt-0 border-primary/30 bg-primary/5 text-primary hover:bg-primary/10 transition-colors duration-200"
                    >
                      {resource.type}
                    </Badge>
                    {user && (
                      <Button
                        variant="ghost"
                        size="icon"
                        className={`p-1 transition-all duration-200 ${
                          bookmarkedResources.has(resource.id)
                            ? 'text-yellow-600 dark:text-yellow-400 hover:bg-yellow-100 dark:hover:bg-yellow-900/30'
                            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-900/30'
                        }`}
                        title={bookmarkedResources.has(resource.id) ? "Remove Bookmark" : "Add Bookmark"}
                        onClick={() => handleBookmark(resource.id)}
                      >
                        {bookmarkedResources.has(resource.id) ? (
                          <BookmarkCheck className="h-4 w-4" />
                        ) : (
                          <Bookmark className="h-4 w-4" />
                        )}
                      </Button>
                    )}
                    {user && user.role === 'admin' && (
                      <>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/30 p-1 transition-all duration-200"
                          title="Edit Resource"
                          onClick={() => handleEditResource(resource)}
                        >
                          <Plus className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/30 p-1 transition-all duration-200"
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
                <p className="text-xs sm:text-sm text-muted-foreground mb-2 sm:mb-4 line-clamp-2">
                  {resource.description}
                </p>
                <div className="flex flex-wrap gap-1 sm:gap-2 mb-2 sm:mb-4">
                  <Badge variant="secondary" className="text-xs sm:text-sm bg-secondary/50 text-secondary-foreground">
                    {resource.department}
                  </Badge>
                  <Badge variant="secondary" className="text-xs sm:text-sm bg-secondary/50 text-secondary-foreground">
                    {resource.year}
                  </Badge>
                  {resource.semester && (
                    <Badge variant="secondary" className="text-xs sm:text-sm bg-secondary/50 text-secondary-foreground">
                      {resource.semester === 'all' ? 'All Semesters' : resource.semester}
                    </Badge>
                  )}
                </div>
                <div className="flex flex-col sm:flex-row justify-between items-center gap-2 sm:gap-0">
                  <div className="text-xs text-muted-foreground">
                    {new Date(resource.uploadedAt).toLocaleDateString()}
                  </div>
                  {resource.gdriveLink ? (
                    <a
                      href={resource.gdriveLink}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 dark:from-blue-500 dark:to-blue-600 dark:hover:from-blue-600 dark:hover:to-blue-700 w-full sm:w-auto text-xs sm:text-sm px-3 py-2 rounded-md text-white flex items-center justify-center transition-all duration-200 transform hover:scale-105 shadow-md hover:shadow-lg"
                    >
                      <Download className="h-4 w-4 mr-1 sm:mr-2" />
                      View on Google Drive
                    </a>
                  ) : (
                    <Button
                      size="sm"
                      onClick={() => handleDownload(resource)}
                      className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 dark:from-green-500 dark:to-green-600 dark:hover:from-green-600 dark:hover:to-green-700 w-full sm:w-auto text-xs sm:text-sm transition-all duration-200 transform hover:scale-105 shadow-md hover:shadow-lg"
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
          <div className="text-center py-8 sm:py-12 animate-fade-in">
            <div className="bg-card/50 dark:bg-card/30 backdrop-blur-md rounded-xl p-8 border border-border">
              <FileText className="h-12 w-12 sm:h-16 sm:w-16 text-muted-foreground mx-auto mb-2 sm:mb-4" />
              <h3 className="text-base sm:text-lg font-medium text-foreground mb-1 sm:mb-2">
                No resources found
              </h3>
              <p className="text-xs sm:text-base text-muted-foreground">
                Try adjusting your search criteria or upload new resources.
              </p>
            </div>
          </div>
        )}
      </main>

      {/* Upload Modal - Enhanced */}
      <Dialog open={showUploadModal} onOpenChange={setShowUploadModal}>
        <DialogContent className="w-full max-w-sm sm:max-w-md md:max-w-lg p-4 sm:p-6 bg-card/95 dark:bg-card/95 backdrop-blur-md border-border overflow-y-auto max-h-[90vh]">
          <DialogHeader>
            <DialogTitle className="text-base sm:text-lg text-card-foreground">Upload Academic Resource</DialogTitle>
            <DialogDescription className="text-xs sm:text-sm text-muted-foreground">
              Share your study materials with fellow students at SXC
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleUpload} className="space-y-3 sm:space-y-4">
            <div>
              <Label htmlFor="title" className="text-sm font-medium text-foreground">Title</Label>
              <Input 
                id="title" 
                name="title" 
                placeholder="e.g., Data Structures Notes" 
                className="text-sm sm:text-base bg-background/50 border-border focus:border-primary transition-colors duration-200" 
              />
            </div>
            <div>
              <Label htmlFor="description" className="text-sm font-medium text-foreground">Description</Label>
              <Textarea 
                id="description" 
                name="description" 
                placeholder="Brief description of the resource" 
                className="text-sm sm:text-base bg-background/50 border-border focus:border-primary transition-colors duration-200" 
              />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
              <div>
                <Label htmlFor="subject" className="text-sm font-medium text-foreground">Subject</Label>
                <Input 
                  id="subject" 
                  name="subject" 
                  placeholder="e.g., Computer Science" 
                  className="text-sm sm:text-base bg-background/50 border-border focus:border-primary transition-colors duration-200" 
                />
              </div>
              <div>
                <Label htmlFor="department" className="text-sm font-medium text-foreground">Department</Label>
                <Select name="department">
                  <SelectTrigger className="text-sm sm:text-base bg-background/50 border-border focus:border-primary">
                    <SelectValue placeholder="Select Department" />
                  </SelectTrigger>
                  <SelectContent className="bg-popover/95 backdrop-blur-md border-border">
                    {departments.map(dept => (
                      <SelectItem key={dept} value={dept}>{dept}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
              <div>
                <Label htmlFor="year" className="text-sm font-medium text-foreground">Year</Label>
                <Select name="year">
                  <SelectTrigger className="text-sm sm:text-base bg-background/50 border-border focus:border-primary">
                    <SelectValue placeholder="Select Year" />
                  </SelectTrigger>
                  <SelectContent className="bg-popover/95 backdrop-blur-md border-border">
                    {years.map(year => (
                      <SelectItem key={year} value={year}>{year}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="semester" className="text-sm font-medium text-foreground">Semester</Label>
                <Select name="semester">
                  <SelectTrigger className="text-sm sm:text-base bg-background/50 border-border focus:border-primary">
                    <SelectValue placeholder="Select Semester" />
                  </SelectTrigger>
                  <SelectContent className="bg-popover/95 backdrop-blur-md border-border">
                    <SelectItem value="all">All Semesters</SelectItem>
                    {semesters.map(sem => (
                      <SelectItem key={sem} value={sem}>{sem}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label htmlFor="type" className="text-sm font-medium text-foreground">Type</Label>
              <Select name="type">
                <SelectTrigger className="text-sm sm:text-base bg-background/50 border-border focus:border-primary">
                  <SelectValue placeholder="Select Type" />
                </SelectTrigger>
                <SelectContent className="bg-popover/95 backdrop-blur-md border-border">
                  {resourceTypes.map(type => (
                    <SelectItem key={type} value={type}>{type}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="file" className="text-sm font-medium text-foreground">File</Label>
              <Input 
                id="file" 
                name="file" 
                type="file" 
                accept=".pdf,.doc,.docx,.ppt,.pptx" 
                className="text-sm sm:text-base bg-background/50 border-border focus:border-primary transition-colors duration-200" 
              />
              <div className="text-xs text-muted-foreground mt-1">
                Or provide a Google Drive link below instead of uploading a file.
              </div>
              <Input 
                id="gdriveLink" 
                name="gdriveLink" 
                type="url" 
                placeholder="https://drive.google.com/..." 
                className="text-sm sm:text-base mt-2 bg-background/50 border-border focus:border-primary transition-colors duration-200" 
              />
            </div>
            <div className="flex flex-col sm:flex-row justify-end gap-2">
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => setShowUploadModal(false)} 
                className="w-full sm:w-auto text-xs sm:text-sm border-border hover:bg-accent transition-colors duration-200"
              >
                Cancel
              </Button>
              <Button 
                type="submit" 
                disabled={loading} 
                className="w-full sm:w-auto text-xs sm:text-sm bg-gradient-to-r from-primary to-purple-500 hover:from-purple-600 hover:to-primary transition-all duration-200"
              >
                {loading ? 'Uploading...' : 'Upload Resource'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Login/Register Modal - Enhanced */}
      <Dialog open={showLoginModal} onOpenChange={setShowLoginModal}>
        <DialogContent className="w-[95vw] max-w-[95vw] sm:max-w-[400px] p-2 sm:p-6 bg-card/95 dark:bg-card/95 backdrop-blur-md border-border">
          <DialogHeader>
            <DialogTitle className="text-base sm:text-lg text-card-foreground">
              {isLogin ? 'Login' : 'Register'} to SXC ScholarHub
            </DialogTitle>
            <DialogDescription className="text-xs sm:text-sm text-muted-foreground">
              {isLogin ? 'Sign in to your account' : 'Create a new account'}
            </DialogDescription>
          </DialogHeader>
          <Tabs value={isLogin ? 'login' : 'register'} onValueChange={(value) => setIsLogin(value === 'login')}>
            <TabsList className="grid w-full grid-cols-2 bg-muted/50">
              <TabsTrigger value="login" className="text-xs sm:text-sm data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                Login
              </TabsTrigger>
              <TabsTrigger value="register" className="text-xs sm:text-sm data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                Register
              </TabsTrigger>
            </TabsList>
            <TabsContent value="login">
              <form onSubmit={handleLogin} className="space-y-3 sm:space-y-4">
                <div>
                  <Label htmlFor="email" className="text-sm font-medium text-foreground">Email</Label>
                  <Input 
                    id="email" 
                    name="email" 
                    type="email" 
                    required 
                    className="text-sm sm:text-base bg-background/50 border-border focus:border-primary transition-colors duration-200" 
                  />
                </div>
                <div>
                  <Label htmlFor="password" className="text-sm font-medium text-foreground">Password</Label>
                  <Input 
                    id="password" 
                    name="password" 
                    type="password" 
                    required 
                    className="text-sm sm:text-base bg-background/50 border-border focus:border-primary transition-colors duration-200" 
                  />
                </div>
                <Button 
                  type="submit" 
                  className="w-full text-xs sm:text-sm bg-gradient-to-r from-primary to-purple-500 hover:from-purple-600 hover:to-primary transition-all duration-200" 
                  disabled={loading}
                >
                  {loading ? 'Logging in...' : 'Login'}
                </Button>
              </form>
            </TabsContent>
            <TabsContent value="register">
              <form onSubmit={handleRegister} className="space-y-3 sm:space-y-4">
                <div>
                  <Label htmlFor="name" className="text-sm font-medium text-foreground">Full Name</Label>
                  <Input 
                    id="name" 
                    name="name" 
                    required 
                    className="text-sm sm:text-base bg-background/50 border-border focus:border-primary transition-colors duration-200" 
                  />
                </div>
                <div>
                  <Label htmlFor="email" className="text-sm font-medium text-foreground">Email</Label>
                  <Input 
                    id="email" 
                    name="email" 
                    type="email" 
                    required 
                    className="text-sm sm:text-base bg-background/50 border-border focus:border-primary transition-colors duration-200" 
                  />
                </div>
                <div>
                  <Label htmlFor="password" className="text-sm font-medium text-foreground">Password</Label>
                  <Input 
                    id="password" 
                    name="password" 
                    type="password" 
                    required 
                    className="text-sm sm:text-base bg-background/50 border-border focus:border-primary transition-colors duration-200" 
                  />
                </div>
                <div>
                  <Label htmlFor="department" className="text-sm font-medium text-foreground">Department</Label>
                  <Select name="department" required>
                    <SelectTrigger className="text-sm sm:text-base bg-background/50 border-border focus:border-primary">
                      <SelectValue placeholder="Select Department" />
                    </SelectTrigger>
                    <SelectContent className="bg-popover/95 backdrop-blur-md border-border">
                      {departments.map(dept => (
                        <SelectItem key={dept} value={dept}>{dept}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="year" className="text-sm font-medium text-foreground">Year</Label>
                  <Select name="year" required>
                    <SelectTrigger className="text-sm sm:text-base bg-background/50 border-border focus:border-primary">
                      <SelectValue placeholder="Select Year" />
                    </SelectTrigger>
                    <SelectContent className="bg-popover/95 backdrop-blur-md border-border">
                      {years.map(year => (
                        <SelectItem key={year} value={year}>{year}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <Button 
                  type="submit" 
                  className="w-full text-xs sm:text-sm bg-gradient-to-r from-primary to-purple-500 hover:from-purple-600 hover:to-primary transition-all duration-200" 
                  disabled={loading}
                >
                  {loading ? 'Creating Account...' : 'Create Account'}
                </Button>
              </form>
            </TabsContent>
          </Tabs>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog - Enhanced */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent className="w-[90vw] max-w-[350px] bg-card/95 dark:bg-card/95 backdrop-blur-md border-border">
          <DialogHeader>
            <DialogTitle className="text-base text-card-foreground">Confirm Delete</DialogTitle>
            <DialogDescription className="text-xs text-muted-foreground">
              Are you sure you want to delete <span className="font-semibold text-foreground">{resourceToDelete?.title}</span>? 
              This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end gap-2 mt-4">
            <Button 
              variant="outline" 
              onClick={() => setDeleteDialogOpen(false)} 
              className="text-xs border-border hover:bg-accent transition-colors duration-200"
            >
              Cancel
            </Button>
            <Button 
              variant="destructive" 
              onClick={() => handleDeleteResource(resourceToDelete)} 
              disabled={loading} 
              className="text-xs bg-destructive hover:bg-destructive/90 transition-colors duration-200"
            >
              {loading ? 'Deleting...' : 'Delete'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Edit Resource Modal - Enhanced */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="w-[95vw] max-w-[95vw] sm:max-w-[500px] p-2 sm:p-6 bg-card/95 dark:bg-card/95 backdrop-blur-md border-border">
          <DialogHeader>
            <DialogTitle className="text-base sm:text-lg text-card-foreground">Edit Academic Resource</DialogTitle>
            <DialogDescription className="text-xs sm:text-sm text-muted-foreground">
              Update the details of this resource
            </DialogDescription>
          </DialogHeader>
          {resourceToEdit && (
            <form onSubmit={handleEditSubmit} className="space-y-3 sm:space-y-4">
              <div>
                <Label htmlFor="edit-title" className="text-sm font-medium text-foreground">Title</Label>
                <Input 
                  id="edit-title" 
                  name="title" 
                  defaultValue={resourceToEdit.title} 
                  required 
                  className="text-sm sm:text-base bg-background/50 border-border focus:border-primary transition-colors duration-200" 
                />
              </div>
              <div>
                <Label htmlFor="edit-description" className="text-sm font-medium text-foreground">Description</Label>
                <Textarea 
                  id="edit-description" 
                  name="description" 
                  defaultValue={resourceToEdit.description} 
                  className="text-sm sm:text-base bg-background/50 border-border focus:border-primary transition-colors duration-200" 
                />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div>
                  <Label htmlFor="edit-subject" className="text-sm font-medium text-foreground">Subject</Label>
                  <Input 
                    id="edit-subject" 
                    name="subject" 
                    defaultValue={resourceToEdit.subject} 
                    required 
                    className="text-sm sm:text-base bg-background/50 border-border focus:border-primary transition-colors duration-200" 
                  />
                </div>
                <div>
                  <Label htmlFor="edit-department" className="text-sm font-medium text-foreground">Department</Label>
                  <Select name="department" defaultValue={resourceToEdit.department} required>
                    <SelectTrigger className="text-sm sm:text-base bg-background/50 border-border focus:border-primary">
                      <SelectValue placeholder="Select Department" />
                    </SelectTrigger>
                    <SelectContent className="bg-popover/95 backdrop-blur-md border-border">
                      {departments.map(dept => (
                        <SelectItem key={dept} value={dept}>{dept}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div>
                  <Label htmlFor="edit-year" className="text-sm font-medium text-foreground">Year</Label>
                  <Select name="year" defaultValue={resourceToEdit.year} required>
                    <SelectTrigger className="text-sm sm:text-base bg-background/50 border-border focus:border-primary">
                      <SelectValue placeholder="Select Year" />
                    </SelectTrigger>
                    <SelectContent className="bg-popover/95 backdrop-blur-md border-border">
                      {years.map(year => (
                        <SelectItem key={year} value={year}>{year}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="edit-semester" className="text-sm font-medium text-foreground">Semester</Label>
                  <Select name="semester" defaultValue={resourceToEdit.semester} required>
                    <SelectTrigger className="text-sm sm:text-base bg-background/50 border-border focus:border-primary">
                      <SelectValue placeholder="Select Semester" />
                    </SelectTrigger>
                    <SelectContent className="bg-popover/95 backdrop-blur-md border-border">
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
                  <Label htmlFor="edit-type" className="text-sm font-medium text-foreground">Type</Label>
                  <Select name="type" defaultValue={resourceToEdit.type} required>
                    <SelectTrigger className="text-sm sm:text-base bg-background/50 border-border focus:border-primary">
                      <SelectValue placeholder="Select Type" />
                    </SelectTrigger>
                    <SelectContent className="bg-popover/95 backdrop-blur-md border-border">
                      {resourceTypes.map(type => (
                        <SelectItem key={type} value={type}>{type}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="edit-gdriveLink" className="text-sm font-medium text-foreground">Google Drive Link</Label>
                  <Input 
                    id="edit-gdriveLink" 
                    name="gdriveLink" 
                    type="url" 
                    defaultValue={resourceToEdit.gdriveLink} 
                    placeholder="https://drive.google.com/..." 
                    className="text-sm sm:text-base bg-background/50 border-border focus:border-primary transition-colors duration-200" 
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="edit-file" className="text-sm font-medium text-foreground">Replace File (optional)</Label>
                <Input 
                  id="edit-file" 
                  name="file" 
                  type="file" 
                  accept=".pdf,.doc,.docx,.ppt,.pptx" 
                  className="text-sm sm:text-base bg-background/50 border-border focus:border-primary transition-colors duration-200" 
                />
                <div className="text-xs text-muted-foreground mt-1">
                  Leave blank to keep the current file.
                </div>
              </div>
              <div className="flex flex-col sm:flex-row justify-end gap-2">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => setEditDialogOpen(false)} 
                  className="w-full sm:w-auto text-xs sm:text-sm border-border hover:bg-accent transition-colors duration-200"
                >
                  Cancel
                </Button>
                <Button 
                  type="submit" 
                  disabled={loading} 
                  className="w-full sm:w-auto text-xs sm:text-sm bg-gradient-to-r from-primary to-purple-500 hover:from-purple-600 hover:to-primary transition-all duration-200"
                >
                  {loading ? 'Saving...' : 'Save Changes'}
                </Button>
              </div>
            </form>
          )}
        </DialogContent>
      </Dialog>

      {/* Enhanced Footer */}
      <footer className="w-full border-t border-border bg-card/50 dark:bg-card/30 backdrop-blur-md mt-8 py-4">
        <div className="container mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-muted-foreground">
          <div>
            Built by <span className="font-semibold text-foreground">Atul Sahu</span> CS Dept.
          </div>
          <div className="flex gap-4 items-center">
            <a 
              href="https://instagram.com/ofc_atul" 
              target="_blank" 
              rel="noopener noreferrer" 
              title="Instagram" 
              className="hover:text-primary transition-colors duration-200 flex items-center gap-1"
            >
              <Instagram className="h-4 w-4" /> ofc_atul
            </a>
            <a 
              href="https://twitter.com/Ofc-atul" 
              target="_blank" 
              rel="noopener noreferrer" 
              title="Twitter" 
              className="hover:text-primary transition-colors duration-200 flex items-center gap-1"
            >
              <Twitter className="h-4 w-4" /> Ofc-atul
            </a>
            <a 
              href="https://github.com/AtulSahu778" 
              target="_blank" 
              rel="noopener noreferrer" 
              title="GitHub" 
              className="hover:text-primary transition-colors duration-200 flex items-center gap-1"
            >
              <Github className="h-4 w-4" /> AtulSahu778
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}