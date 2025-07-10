# State Management: React vs Angular Comparison

## Overview

**Redux Toolkit** = Client-side state management  
**Redux Toolkit Query** = Server-side state management (on the client)

This document compares React's state management approaches with their Angular equivalents.

---

## Client-Side State Management

### React: Redux Toolkit

```typescript
// store/userSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface User {
  id: string;
  name: string;
}

interface UserState {
  selectedUser: User | null;
  showActiveOnly: boolean;
  filterText: string;
}

const initialState: UserState = {
  selectedUser: null,
  showActiveOnly: false,
  filterText: ''
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setSelectedUser: (state, action: PayloadAction<User>) => {
      state.selectedUser = action.payload;
    },
    toggleUserFilter: (state) => {
      state.showActiveOnly = !state.showActiveOnly;
    },
    setFilterText: (state, action: PayloadAction<string>) => {
      state.filterText = action.payload;
    }
  }
});

export const { setSelectedUser, toggleUserFilter, setFilterText } = userSlice.actions;
export default userSlice.reducer;
```

```typescript
// Component usage
import { useAppDispatch, useAppSelector } from '../hooks/redux';
import { setSelectedUser, toggleUserFilter } from '../store/userSlice';

export const UserComponent: React.FC = () => {
  const dispatch = useAppDispatch();
  const { selectedUser, showActiveOnly } = useAppSelector(state => state.user);

  const selectUser = (user: User) => {
    dispatch(setSelectedUser(user));
  };

  const toggleFilter = () => {
    dispatch(toggleUserFilter());
  };

  return (
    <div>
      <p>Selected: {selectedUser?.name}</p>
      <button onClick={toggleFilter}>
        {showActiveOnly ? 'Show All' : 'Show Active Only'}
      </button>
    </div>
  );
};
```

### Angular: NgRx Store (Redux-like)

```typescript
// actions/user.actions.ts
import { createAction, props } from '@ngrx/store';

export const setSelectedUser = createAction(
  '[User] Set Selected User',
  props<{ user: User }>()
);

export const toggleUserFilter = createAction('[User] Toggle Filter');

export const setFilterText = createAction(
  '[User] Set Filter Text',
  props<{ filterText: string }>()
);
```

```typescript
// reducers/user.reducer.ts
import { createReducer, on } from '@ngrx/store';

interface UserState {
  selectedUser: User | null;
  showActiveOnly: boolean;
  filterText: string;
}

const initialState: UserState = {
  selectedUser: null,
  showActiveOnly: false,
  filterText: ''
};

export const userReducer = createReducer(
  initialState,
  on(setSelectedUser, (state, { user }) => ({
    ...state,
    selectedUser: user
  })),
  on(toggleUserFilter, (state) => ({
    ...state,
    showActiveOnly: !state.showActiveOnly
  })),
  on(setFilterText, (state, { filterText }) => ({
    ...state,
    filterText
  }))
);
```

```typescript
// Component usage
import { Component } from '@angular/core';
import { Store } from '@ngrx/store';
import { setSelectedUser, toggleUserFilter } from '../actions/user.actions';

@Component({
  selector: 'app-user',
  template: `
    <div>
      <p>Selected: {{ (selectedUser$ | async)?.name }}</p>
      <button (click)="toggleFilter()">
        {{ (showActiveOnly$ | async) ? 'Show All' : 'Show Active Only' }}
      </button>
    </div>
  `
})
export class UserComponent {
  selectedUser$ = this.store.select(state => state.user.selectedUser);
  showActiveOnly$ = this.store.select(state => state.user.showActiveOnly);
  
  constructor(private store: Store) {}
  
  selectUser(user: User) {
    this.store.dispatch(setSelectedUser({ user }));
  }
  
  toggleFilter() {
    this.store.dispatch(toggleUserFilter());
  }
}
```

### Angular: Signals (Simpler Alternative)

```typescript
// services/user-state.service.ts
import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class UserStateService {
  private _selectedUser = signal<User | null>(null);
  private _showActiveOnly = signal(false);
  private _filterText = signal('');
  
  // Read-only signals
  selectedUser = this._selectedUser.asReadonly();
  showActiveOnly = this._showActiveOnly.asReadonly();
  filterText = this._filterText.asReadonly();
  
  // Actions
  setSelectedUser(user: User) {
    this._selectedUser.set(user);
  }
  
  toggleFilter() {
    this._showActiveOnly.update(show => !show);
  }
  
  setFilterText(text: string) {
    this._filterText.set(text);
  }
}
```

```typescript
// Component usage
import { Component } from '@angular/core';
import { UserStateService } from '../services/user-state.service';

@Component({
  selector: 'app-user',
  template: `
    <div>
      <p>Selected: {{ userState.selectedUser()?.name }}</p>
      <button (click)="toggleFilter()">
        {{ userState.showActiveOnly() ? 'Show All' : 'Show Active Only' }}
      </button>
      <input 
        [value]="userState.filterText()" 
        (input)="setFilterText($event.target.value)"
        placeholder="Filter users..."
      />
    </div>
  `
})
export class UserComponent {
  constructor(public userState: UserStateService) {}
  
  selectUser(user: User) {
    this.userState.setSelectedUser(user);
  }
  
  toggleFilter() {
    this.userState.toggleFilter();
  }
  
  setFilterText(text: string) {
    this.userState.setFilterText(text);
  }
}
```

---

## Server-Side State Management

### React: Redux Toolkit Query

```typescript
// api/userApi.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

interface User {
  id: string;
  name: string;
  email: string;
}

interface CreateUserRequest {
  name: string;
  email: string;
}

export const userApi = createApi({
  reducerPath: 'userApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api/',
  }),
  tagTypes: ['User'],
  endpoints: (builder) => ({
    getUsers: builder.query<User[], void>({
      query: () => 'users',
      providesTags: ['User'],
    }),
    
    getUser: builder.query<User, string>({
      query: (id) => `users/${id}`,
      providesTags: (result, error, id) => [{ type: 'User', id }],
    }),
    
    createUser: builder.mutation<User, CreateUserRequest>({
      query: (newUser) => ({
        url: 'users',
        method: 'POST',
        body: newUser,
      }),
      invalidatesTags: ['User'],
    }),
    
    updateUser: builder.mutation<User, Partial<User> & Pick<User, 'id'>>({
      query: ({ id, ...patch }) => ({
        url: `users/${id}`,
        method: 'PATCH',
        body: patch,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'User', id }],
    }),
    
    deleteUser: builder.mutation<void, string>({
      query: (id) => ({
        url: `users/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['User'],
    }),
  }),
});

export const {
  useGetUsersQuery,
  useGetUserQuery,
  useCreateUserMutation,
  useUpdateUserMutation,
  useDeleteUserMutation,
} = userApi;
```

```typescript
// Component usage
import React from 'react';
import { useGetUsersQuery, useDeleteUserMutation } from '../api/userApi';

export const UserList: React.FC = () => {
  const {
    data: users,
    error,
    isLoading,
    refetch,
  } = useGetUsersQuery();

  const [deleteUser, { isLoading: isDeleting }] = useDeleteUserMutation();

  const handleDelete = async (id: string) => {
    try {
      await deleteUser(id).unwrap();
      console.log('User deleted successfully');
    } catch (error) {
      console.error('Failed to delete user:', error);
    }
  };

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {JSON.stringify(error)}</div>;

  return (
    <div>
      <button onClick={() => refetch()}>Refresh</button>
      {users?.map((user) => (
        <div key={user.id}>
          <h3>{user.name}</h3>
          <p>{user.email}</p>
          <button
            onClick={() => handleDelete(user.id)}
            disabled={isDeleting}
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      ))}
    </div>
  );
};
```

### Angular: HTTP Client + RxJS (Built-in)

```typescript
// services/user-api.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class UserApiService {
  private baseUrl = '/api/users';
  
  constructor(private http: HttpClient) {}
  
  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(this.baseUrl);
  }
  
  getUser(id: string): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/${id}`);
  }
  
  createUser(user: CreateUserRequest): Observable<User> {
    return this.http.post<User>(this.baseUrl, user);
  }
  
  updateUser(id: string, user: Partial<User>): Observable<User> {
    return this.http.put<User>(`${this.baseUrl}/${id}`, user);
  }
  
  deleteUser(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }
}
```

```typescript
// Component usage with RxJS
import { Component, OnInit } from '@angular/core';
import { UserApiService } from '../services/user-api.service';

@Component({
  selector: 'app-user-list',
  template: `
    <div>
      <div *ngIf="loading">Loading...</div>
      <div *ngIf="error">Error: {{ error }}</div>
      <button (click)="loadUsers()">Refresh</button>
      
      <div *ngFor="let user of users">
        <h3>{{ user.name }}</h3>
        <p>{{ user.email }}</p>
        <button (click)="deleteUser(user.id)">Delete</button>
      </div>
    </div>
  `
})
export class UserListComponent implements OnInit {
  users: User[] = [];
  loading = false;
  error: string | null = null;
  
  constructor(private userApi: UserApiService) {}
  
  ngOnInit() {
    this.loadUsers();
  }
  
  loadUsers() {
    this.loading = true;
    this.error = null;
    
    this.userApi.getUsers().subscribe({
      next: (users) => {
        this.users = users;
        this.loading = false;
      },
      error: (error) => {
        this.error = error.message;
        this.loading = false;
      }
    });
  }
  
  deleteUser(id: string) {
    this.userApi.deleteUser(id).subscribe({
      next: () => {
        this.users = this.users.filter(user => user.id !== id);
      },
      error: (error) => {
        this.error = error.message;
      }
    });
  }
}
```

### Angular: HTTP Client + Signals (Modern)

```typescript
// services/user-data.service.ts
import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class UserDataService {
  private _users = signal<User[]>([]);
  private _loading = signal(false);
  private _error = signal<string | null>(null);
  
  // Read-only signals
  users = this._users.asReadonly();
  loading = this._loading.asReadonly();
  error = this._error.asReadonly();
  
  constructor(private http: HttpClient, private userApi: UserApiService) {}
  
  async loadUsers() {
    this._loading.set(true);
    this._error.set(null);
    
    try {
      const users = await firstValueFrom(this.userApi.getUsers());
      this._users.set(users);
    } catch (error) {
      this._error.set(error.message);
    } finally {
      this._loading.set(false);
    }
  }
  
  async createUser(user: CreateUserRequest) {
    try {
      const newUser = await firstValueFrom(this.userApi.createUser(user));
      this._users.update(users => [...users, newUser]);
      return newUser;
    } catch (error) {
      this._error.set(error.message);
      throw error;
    }
  }
  
  async deleteUser(id: string) {
    try {
      await firstValueFrom(this.userApi.deleteUser(id));
      this._users.update(users => users.filter(user => user.id !== id));
    } catch (error) {
      this._error.set(error.message);
      throw error;
    }
  }
}
```

```typescript
// Component usage with Signals
import { Component, OnInit } from '@angular/core';
import { UserDataService } from '../services/user-data.service';

@Component({
  selector: 'app-user-list',
  template: `
    <div>
      @if (userData.loading()) {
        <div>Loading...</div>
      }
      @if (userData.error()) {
        <div>Error: {{ userData.error() }}</div>
      }
      
      <button (click)="refresh()">Refresh</button>
      
      @for (user of userData.users(); track user.id) {
        <div>
          <h3>{{ user.name }}</h3>
          <p>{{ user.email }}</p>
          <button (click)="deleteUser(user.id)">Delete</button>
        </div>
      }
    </div>
  `
})
export class UserListComponent implements OnInit {
  constructor(public userData: UserDataService) {}
  
  ngOnInit() {
    this.userData.loadUsers();
  }
  
  refresh() {
    this.userData.loadUsers();
  }
  
  async deleteUser(id: string) {
    try {
      await this.userData.deleteUser(id);
    } catch (error) {
      console.error('Delete failed:', error);
    }
  }
}
```

### Angular: Third-party Query Library

```bash
# Install Angular Query (like React Query)
npm install @ngneat/query
```

```typescript
// services/user-queries.service.ts
import { Injectable } from '@angular/core';
import { QueryService } from '@ngneat/query';
import { UserApiService } from './user-api.service';

@Injectable({ providedIn: 'root' })
export class UserQueriesService {
  constructor(
    private query: QueryService,
    private userApi: UserApiService
  ) {}
  
  getUsers() {
    return this.query.use({
      queryKey: ['users'],
      queryFn: () => this.userApi.getUsers()
    });
  }
  
  getUser(id: string) {
    return this.query.use({
      queryKey: ['users', id],
      queryFn: () => this.userApi.getUser(id)
    });
  }
  
  createUser() {
    return this.query.useMutation({
      mutationFn: (user: CreateUserRequest) => this.userApi.createUser(user),
      onSuccess: () => {
        this.query.invalidateQueries(['users']);
      }
    });
  }
  
  deleteUser() {
    return this.query.useMutation({
      mutationFn: (id: string) => this.userApi.deleteUser(id),
      onSuccess: () => {
        this.query.invalidateQueries(['users']);
      }
    });
  }
}
```

```typescript
// Component usage with Angular Query
import { Component } from '@angular/core';
import { UserQueriesService } from '../services/user-queries.service';

@Component({
  selector: 'app-user-list',
  template: `
    <div>
      @if (usersQuery.isLoading) {
        <div>Loading...</div>
      }
      @if (usersQuery.error) {
        <div>Error: {{ usersQuery.error.message }}</div>
      }
      
      <button (click)="usersQuery.refetch()">Refresh</button>
      
      @for (user of usersQuery.data || []; track user.id) {
        <div>
          <h3>{{ user.name }}</h3>
          <p>{{ user.email }}</p>
          <button 
            (click)="deleteUser(user.id)"
            [disabled]="deleteMutation.isLoading"
          >
            {{ deleteMutation.isLoading ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      }
    </div>
  `
})
export class UserListComponent {
  usersQuery = this.userQueries.getUsers();
  deleteMutation = this.userQueries.deleteUser();
  
  constructor(private userQueries: UserQueriesService) {}
  
  deleteUser(id: string) {
    this.deleteMutation.mutate(id);
  }
}
```

---

## Summary Comparison

| Concern | React | Angular |
|---------|-------|---------|
| **Client State (Simple)** | useState + Context | Signals |
| **Client State (Complex)** | Redux Toolkit | NgRx Store |
| **Server State (Built-in)** | fetch + useState | HTTP Client + RxJS/Signals |
| **Server State (Advanced)** | RTK Query / React Query | @ngneat/query |

## When to Use What

### Client State Management

**Use Signals when:**
- Simple to medium complexity
- Local component state
- Modern Angular (v16+)
- Want automatic reactivity

**Use NgRx when:**
- Complex application state
- Multiple components sharing state
- Need time-travel debugging
- Enterprise applications
- Team prefers Redux patterns

### Server State Management

**Use HTTP Client + Signals/RxJS when:**
- Simple API calls
- Don't need advanced caching
- Want to stick with Angular built-ins
- Small to medium applications

**Use Third-party Query Library when:**
- Need advanced caching strategies
- Background refetching required
- Optimistic updates needed
- Complex synchronization requirements
- Large applications with many API calls

---

## Best Practices

1. **Start Simple**: Begin with Signals for client state, HTTP Client for server state
2. **Scale Up**: Add NgRx or query libraries as complexity grows
3. **Separate Concerns**: Keep client state and server state management separate
4. **Type Safety**: Always use TypeScript interfaces for state shapes
5. **Error Handling**: Implement consistent error handling patterns
6. **Testing**: Write tests for state logic, especially with complex state management

Similar code found with 1 license type