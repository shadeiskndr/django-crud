# Angular State Management Guide

A comprehensive guide to managing state in Angular applications using RxJS Observables, Signals, and global state management solutions.

## Table of Contents
- [When to Use Each Approach](#when-to-use-each-approach)
- [Signals](#signals)
- [RxJS Observables](#rxjs-observables)
- [Global State Management](#global-state-management)
- [RxJS Deep Dive](#rxjs-deep-dive)
- [Best Practices](#best-practices)
- [Migration Strategies](#migration-strategies)
- [Performance Considerations](#performance-considerations)

## When to Use Each Approach

| Scenario | Signals | RxJS Observables | Global State (NgRx/Custom) |
|----------|---------|------------------|----------------------------|
| Component local state | ✅ Best choice | ❌ Overkill | ❌ Overkill |
| Derived/computed state | ✅ Best choice | ⚠️ Possible but complex | ❌ Not suitable |
| Simple async operations | ⚠️ Manual handling | ✅ Best choice | ❌ Overkill |
| Complex async flows | ❌ Limited | ✅ Best choice | ⚠️ If global |
| Cross-component state | ⚠️ Via services | ⚠️ Via services | ✅ Best choice |
| State persistence | ⚠️ Manual | ⚠️ Manual | ✅ Built-in patterns |
| Time-travel debugging | ❌ Not available | ❌ Limited | ✅ Available |
| Performance critical | ✅ Fine-grained | ⚠️ Can be heavy | ⚠️ Depends on implementation |

## Signals

### What are Signals?
Signals are Angular's new reactive primitive (Angular 17+) for managing synchronous reactive state with fine-grained reactivity.

### Basic Usage

```typescript
import { signal, computed, effect } from '@angular/core';

export class UserComponent {
  // Basic signal
  userName = signal('John Doe');
  age = signal(25);
  isLoading = signal(false);
  
  // Computed signal (derived state)
  displayName = computed(() => 
    `${this.userName()} (${this.age()} years old)`
  );
  
  // Array signal
  todos = signal<Todo[]>([]);
  
  // Computed from array
  completedTodos = computed(() => 
    this.todos().filter(todo => todo.completed)
  );
  
  constructor() {
    // Effect - runs when signals change
    effect(() => {
      console.log('User changed:', this.displayName());
    });
  }
  
  // Methods to update signals
  updateUserName(name: string) {
    this.userName.set(name);
  }
  
  incrementAge() {
    this.age.update(current => current + 1);
  }
  
  addTodo(todo: Todo) {
    this.todos.update(current => [...current, todo]);
  }
  
  toggleTodo(id: string) {
    this.todos.update(todos => 
      todos.map(todo => 
        todo.id === id 
          ? { ...todo, completed: !todo.completed }
          : todo
      )
    );
  }
}
```

### Signal API Reference

```typescript
// Creating signals
const count = signal(0);                    // Writable signal
const readOnlyCount = count.asReadonly();   // Read-only signal

// Reading signals
console.log(count());                       // Get current value

// Writing signals
count.set(10);                             // Set new value
count.update(current => current + 1);     // Update based on current

// Computed signals
const doubled = computed(() => count() * 2);

// Effects
effect(() => {
  console.log('Count is:', count());
});

// Converting between Signals and Observables
const count$ = toObservable(count);        // Signal to Observable
const fromObs = toSignal(observable$);     // Observable to Signal
```

### Advanced Signal Patterns

```typescript
// Custom signal-based service
@Injectable({ providedIn: 'root' })
export class UserService {
  private _users = signal<User[]>([]);
  private _selectedUserId = signal<string | null>(null);
  private _isLoading = signal(false);
  
  // Public read-only signals
  users = this._users.asReadonly();
  selectedUserId = this._selectedUserId.asReadonly();
  isLoading = this._isLoading.asReadonly();
  
  // Computed signals
  selectedUser = computed(() => {
    const id = this._selectedUserId();
    return id ? this._users().find(u => u.id === id) : null;
  });
  
  userCount = computed(() => this._users().length);
  
  // Methods
  async loadUsers() {
    this._isLoading.set(true);
    try {
      const users = await this.http.get<User[]>('/api/users').toPromise();
      this._users.set(users);
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
      this._isLoading.set(false);
    }
  }
  
  selectUser(userId: string) {
    this._selectedUserId.set(userId);
  }
  
  addUser(user: User) {
    this._users.update(current => [...current, user]);
  }
  
  updateUser(updatedUser: User) {
    this._users.update(current =>
      current.map(user => 
        user.id === updatedUser.id ? updatedUser : user
      )
    );
  }
  
  deleteUser(userId: string) {
    this._users.update(current => 
      current.filter(user => user.id !== userId)
    );
  }
}
```

## RxJS Observables

### What is RxJS?
RxJS (Reactive Extensions for JavaScript) is a library for reactive programming using Observables. It provides a powerful way to handle asynchronous data streams and events.

### Core RxJS Components

#### 1. Observables
```typescript
import { Observable } from 'rxjs';

// Creating Observables
const observable = new Observable<string>(subscriber => {
  subscriber.next('Hello');
  subscriber.next('World');
  subscriber.complete();
});

// Subscribing
observable.subscribe({
  next: value => console.log(value),
  error: err => console.error(err),
  complete: () => console.log('Complete')
});
```

#### 2. Subjects
```typescript
import { Subject, BehaviorSubject, ReplaySubject, AsyncSubject } from 'rxjs';

// Subject - Basic multicast Observable
const subject = new Subject<string>();
subject.subscribe(value => console.log('Subscriber 1:', value));
subject.subscribe(value => console.log('Subscriber 2:', value));
subject.next('Hello'); // Both subscribers receive

// BehaviorSubject - Stores current value
const behaviorSubject = new BehaviorSubject<string>('Initial');
behaviorSubject.subscribe(value => console.log('Late subscriber:', value)); // Gets 'Initial'
behaviorSubject.next('Updated');

// ReplaySubject - Replays last N values
const replaySubject = new ReplaySubject<string>(2); // Last 2 values
replaySubject.next('First');
replaySubject.next('Second');
replaySubject.next('Third');
replaySubject.subscribe(value => console.log(value)); // Gets 'Second', 'Third'

// AsyncSubject - Only emits last value on complete
const asyncSubject = new AsyncSubject<string>();
asyncSubject.next('First');
asyncSubject.next('Last');
asyncSubject.complete(); // Subscribers get 'Last'
```

#### 3. Creation Operators
```typescript
import { of, from, interval, timer, fromEvent, ajax, defer, range } from 'rxjs';

// of - Emit sequence of values
const numbers$ = of(1, 2, 3, 4, 5);

// from - Convert Promise, Array, or Iterable to Observable
const fromArray$ = from([1, 2, 3]);
const fromPromise$ = from(fetch('/api/data'));

// interval - Emit incremental numbers periodically
const timer$ = interval(1000); // Every second

// timer - Emit single value after delay
const delayed$ = timer(2000); // After 2 seconds

// fromEvent - Convert DOM events to Observable
const clicks$ = fromEvent(document, 'click');

// range - Emit range of numbers
const range$ = range(1, 10); // 1 to 10

// defer - Create Observable lazily
const deferred$ = defer(() => of(Math.random()));
```

#### 4. Transformation Operators
```typescript
import { map, mergeMap, switchMap, concatMap, exhaustMap, scan, reduce } from 'rxjs/operators';

// map - Transform each value
numbers$.pipe(
  map(x => x * 2)
);

// mergeMap - Map to Observable and merge
searchTerm$.pipe(
  mergeMap(term => this.searchService.search(term))
);

// switchMap - Map to Observable, cancel previous
searchTerm$.pipe(
  switchMap(term => this.searchService.search(term)) // Cancel previous search
);

// concatMap - Map to Observable, wait for previous to complete
requests$.pipe(
  concatMap(req => this.http.post('/api', req)) // Process in order
);

// exhaustMap - Map to Observable, ignore new while current is active
button$.pipe(
  exhaustMap(() => this.saveData()) // Ignore clicks while saving
);

// scan - Accumulate over time (like reduce but emits intermediate values)
clicks$.pipe(
  scan((count, click) => count + 1, 0) // Count clicks
);
```

#### 5. Filtering Operators
```typescript
import { 
  filter, take, skip, first, last, 
  debounceTime, throttleTime, distinctUntilChanged,
  takeUntil, takeWhile, skipUntil, skipWhile
} from 'rxjs/operators';

// filter - Emit only values that pass predicate
numbers$.pipe(
  filter(x => x > 5)
);

// take - Take first N values
numbers$.pipe(
  take(3) // First 3 values
);

// debounceTime - Emit after silence period
searchInput$.pipe(
  debounceTime(300) // Wait 300ms after last keystroke
);

// throttleTime - Emit at most once per time period
scrollEvents$.pipe(
  throttleTime(100) // At most once per 100ms
);

// distinctUntilChanged - Emit only when value changes
formValue$.pipe(
  distinctUntilChanged() // Only when form actually changes
);

// takeUntil - Take until another Observable emits
dataStream$.pipe(
  takeUntil(this.destroy$) // Until component destroys
);
```

#### 6. Combination Operators
```typescript
import { merge, concat, zip, combineLatest, withLatestFrom, startWith } from 'rxjs';

// merge - Merge multiple Observables
const merged$ = merge(obs1$, obs2$, obs3$);

// combineLatest - Combine latest values from all Observables
const combined$ = combineLatest([name$, age$, email$]).pipe(
  map(([name, age, email]) => ({ name, age, email }))
);

// zip - Combine values by position
const zipped$ = zip(numbers$, letters$).pipe(
  map(([num, letter]) => `${num}${letter}`)
);

// withLatestFrom - Combine with latest from other Observables
button$.pipe(
  withLatestFrom(formValue$),
  map(([click, formData]) => formData)
);

// startWith - Start with initial value
data$.pipe(
  startWith(null) // Start with null before data loads
);
```

#### 7. Error Handling
```typescript
import { catchError, retry, retryWhen, throwError } from 'rxjs';

// catchError - Handle errors gracefully
this.http.get('/api/data').pipe(
  catchError(error => {
    console.error('API Error:', error);
    return of([]); // Return empty array on error
  })
);

// retry - Retry on error
this.http.get('/api/data').pipe(
  retry(3) // Retry up to 3 times
);

// retryWhen - Custom retry logic
this.http.get('/api/data').pipe(
  retryWhen(errors => 
    errors.pipe(
      delay(1000), // Wait 1 second
      take(3) // Only retry 3 times
    )
  )
);
```

#### 8. Utility Operators
```typescript
import { tap, delay, timeout, finalize, share, shareReplay } from 'rxjs/operators';

// tap - Side effects without changing the stream
data$.pipe(
  tap(data => console.log('Data received:', data)),
  map(data => data.items)
);

// delay - Delay emissions
data$.pipe(
  delay(1000) // Delay by 1 second
);

// timeout - Error if no emission within time
data$.pipe(
  timeout(5000) // Error if no data within 5 seconds
);

// finalize - Execute on complete or error
data$.pipe(
  finalize(() => this.isLoading.set(false))
);

// share - Share single subscription among multiple subscribers
const shared$ = expensiveOperation$.pipe(share());

// shareReplay - Share and replay last N values
const cached$ = this.http.get('/api/config').pipe(
  shareReplay(1) // Cache last response
);
```

### Angular-Specific RxJS Patterns

```typescript
// HTTP with error handling and loading state
@Injectable({ providedIn: 'root' })
export class DataService {
  private loadingSubject = new BehaviorSubject<boolean>(false);
  loading$ = this.loadingSubject.asObservable();
  
  getData() {
    this.loadingSubject.next(true);
    return this.http.get<any[]>('/api/data').pipe(
      finalize(() => this.loadingSubject.next(false)),
      catchError(error => {
        console.error('Error loading data:', error);
        return of([]);
      })
    );
  }
  
  // Search with debounce
  search(term$: Observable<string>) {
    return term$.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      switchMap(term => 
        term.length > 2 
          ? this.http.get<any[]>(`/api/search?q=${term}`)
          : of([])
      ),
      catchError(() => of([]))
    );
  }
}

// Component lifecycle management
export class MyComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  
  ngOnInit() {
    // Auto-unsubscribe when component destroys
    this.dataService.getData().pipe(
      takeUntil(this.destroy$)
    ).subscribe(data => {
      // Handle data
    });
    
    // Form value changes
    this.form.valueChanges.pipe(
      takeUntil(this.destroy$),
      debounceTime(300)
    ).subscribe(value => {
      // Handle form changes
    });
  }
  
  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

## Global State Management

### Option 1: NgRx (External Library)

NgRx is the most popular state management library for Angular, inspired by Redux.

#### Installation
```bash
npm install @ngrx/store @ngrx/effects @ngrx/entity @ngrx/store-devtools
```

#### Basic Setup
```typescript
// State interface
export interface AppState {
  users: UserState;
  products: ProductState;
}

export interface UserState {
  users: User[];
  selectedUser: User | null;
  loading: boolean;
  error: string | null;
}

// Actions
export const loadUsers = createAction('[User] Load Users');
export const loadUsersSuccess = createAction(
  '[User] Load Users Success',
  props<{ users: User[] }>()
);
export const loadUsersFailure = createAction(
  '[User] Load Users Failure',
  props<{ error: string }>()
);

// Reducer
const initialState: UserState = {
  users: [],
  selectedUser: null,
  loading: false,
  error: null
};

export const userReducer = createReducer(
  initialState,
  on(loadUsers, state => ({
    ...state,
    loading: true,
    error: null
  })),
  on(loadUsersSuccess, (state, { users }) => ({
    ...state,
    users,
    loading: false
  })),
  on(loadUsersFailure, (state, { error }) => ({
    ...state,
    error,
    loading: false
  }))
);

// Effects
@Injectable()
export class UserEffects {
  loadUsers$ = createEffect(() =>
    this.actions$.pipe(
      ofType(loadUsers),
      switchMap(() =>
        this.userService.getUsers().pipe(
          map(users => loadUsersSuccess({ users })),
          catchError(error => of(loadUsersFailure({ error: error.message })))
        )
      )
    )
  );
  
  constructor(
    private actions$: Actions,
    private userService: UserService
  ) {}
}

// Selectors
export const selectUserState = (state: AppState) => state.users;
export const selectUsers = createSelector(
  selectUserState,
  state => state.users
);
export const selectLoading = createSelector(
  selectUserState,
  state => state.loading
);

// Component usage
@Component({})
export class UserListComponent {
  users$ = this.store.select(selectUsers);
  loading$ = this.store.select(selectLoading);
  
  constructor(private store: Store<AppState>) {}
  
  ngOnInit() {
    this.store.dispatch(loadUsers());
  }
}
```

### Option 2: Custom Service with Signals

```typescript
@Injectable({ providedIn: 'root' })
export class UserStateService {
  // Private signals
  private _users = signal<User[]>([]);
  private _selectedUserId = signal<string | null>(null);
  private _loading = signal(false);
  private _error = signal<string | null>(null);
  
  // Public read-only signals
  users = this._users.asReadonly();
  selectedUserId = this._selectedUserId.asReadonly();
  loading = this._loading.asReadonly();
  error = this._error.asReadonly();
  
  // Computed signals
  selectedUser = computed(() => {
    const id = this._selectedUserId();
    return id ? this._users().find(u => u.id === id) || null : null;
  });
  
  userCount = computed(() => this._users().length);
  
  hasUsers = computed(() => this._users().length > 0);
  
  constructor(private userService: UserService) {}
  
  // Actions
  async loadUsers() {
    if (this._loading()) return; // Prevent duplicate calls
    
    this._loading.set(true);
    this._error.set(null);
    
    try {
      const users = await this.userService.getUsers().toPromise();
      this._users.set(users);
    } catch (error) {
      this._error.set(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      this._loading.set(false);
    }
  }
  
  selectUser(userId: string | null) {
    this._selectedUserId.set(userId);
  }
  
  addUser(user: User) {
    this._users.update(current => [...current, user]);
  }
  
  updateUser(updatedUser: User) {
    this._users.update(current =>
      current.map(user => 
        user.id === updatedUser.id ? updatedUser : user
      )
    );
  }
  
  deleteUser(userId: string) {
    this._users.update(current => 
      current.filter(user => user.id !== userId)
    );
    
    // Clear selection if deleted user was selected
    if (this._selectedUserId() === userId) {
      this._selectedUserId.set(null);
    }
  }
  
  // Reset state
  reset() {
    this._users.set([]);
    this._selectedUserId.set(null);
    this._loading.set(false);
    this._error.set(null);
  }
}

// Component usage
@Component({
  template: `
    <div *ngIf="userState.loading()">Loading...</div>
    <div *ngIf="userState.error()" class="error">{{ userState.error() }}</div>
    
    <div *ngFor="let user of userState.users()" 
         [class.selected]="user.id === userState.selectedUserId()"
         (click)="userState.selectUser(user.id)">
      {{ user.name }}
    </div>
    
    <p>Total users: {{ userState.userCount() }}</p>
  `
})
export class UserListComponent implements OnInit {
  constructor(public userState: UserStateService) {}
  
  ngOnInit() {
    this.userState.loadUsers();
  }
}
```

### Option 3: Custom Service with BehaviorSubject

```typescript
@Injectable({ providedIn: 'root' })
export class UserStateService {
  private usersSubject = new BehaviorSubject<User[]>([]);
  private selectedUserIdSubject = new BehaviorSubject<string | null>(null);
  private loadingSubject = new BehaviorSubject<boolean>(false);
  private errorSubject = new BehaviorSubject<string | null>(null);
  
  // Public observables
  users$ = this.usersSubject.asObservable();
  selectedUserId$ = this.selectedUserIdSubject.asObservable();
  loading$ = this.loadingSubject.asObservable();
  error$ = this.errorSubject.asObservable();
  
  // Computed observables
  selectedUser$ = combineLatest([this.users$, this.selectedUserId$]).pipe(
    map(([users, selectedId]) => 
      selectedId ? users.find(u => u.id === selectedId) || null : null
    )
  );
  
  userCount$ = this.users$.pipe(map(users => users.length));
  
  constructor(private userService: UserService) {}
  
  loadUsers() {
    if (this.loadingSubject.value) return;
    
    this.loadingSubject.next(true);
    this.errorSubject.next(null);
    
    this.userService.getUsers().pipe(
      finalize(() => this.loadingSubject.next(false))
    ).subscribe({
      next: users => this.usersSubject.next(users),
      error: error => this.errorSubject.next(error.message)
    });
  }
  
  selectUser(userId: string | null) {
    this.selectedUserIdSubject.next(userId);
  }
  
  addUser(user: User) {
    const currentUsers = this.usersSubject.value;
    this.usersSubject.next([...currentUsers, user]);
  }
  
  updateUser(updatedUser: User) {
    const currentUsers = this.usersSubject.value;
    this.usersSubject.next(
      currentUsers.map(user => 
        user.id === updatedUser.id ? updatedUser : user
      )
    );
  }
  
  deleteUser(userId: string) {
    const currentUsers = this.usersSubject.value;
    this.usersSubject.next(currentUsers.filter(user => user.id !== userId));
    
    if (this.selectedUserIdSubject.value === userId) {
      this.selectedUserIdSubject.next(null);
    }
  }
}
```

### Option 4: Browser Storage Integration

```typescript
@Injectable({ providedIn: 'root' })
export class PersistentStateService {
  private readonly STORAGE_KEY = 'app-state';
  
  // Load initial state from localStorage
  private _theme = signal(this.getStoredValue('theme', 'light'));
  private _language = signal(this.getStoredValue('language', 'en'));
  private _userPreferences = signal(this.getStoredValue('userPreferences', {}));
  
  // Public read-only signals
  theme = this._theme.asReadonly();
  language = this._language.asReadonly();
  userPreferences = this._userPreferences.asReadonly();
  
  constructor() {
    // Auto-save to localStorage when signals change
    effect(() => {
      this.saveToStorage('theme', this._theme());
    });
    
    effect(() => {
      this.saveToStorage('language', this._language());
    });
    
    effect(() => {
      this.saveToStorage('userPreferences', this._userPreferences());
    });
  }
  
  setTheme(theme: string) {
    this._theme.set(theme);
  }
  
  setLanguage(language: string) {
    this._language.set(language);
  }
  
  updateUserPreferences(preferences: Partial<UserPreferences>) {
    this._userPreferences.update(current => ({
      ...current,
      ...preferences
    }));
  }
  
  private getStoredValue<T>(key: string, defaultValue: T): T {
    try {
      const stored = localStorage.getItem(`${this.STORAGE_KEY}-${key}`);
      return stored ? JSON.parse(stored) : defaultValue;
    } catch {
      return defaultValue;
    }
  }
  
  private saveToStorage<T>(key: string, value: T) {
    try {
      localStorage.setItem(`${this.STORAGE_KEY}-${key}`, JSON.stringify(value));
    } catch (error) {
      console.warn('Failed to save to localStorage:', error);
    }
  }
  
  clearStorage() {
    Object.keys(localStorage)
      .filter(key => key.startsWith(this.STORAGE_KEY))
      .forEach(key => localStorage.removeItem(key));
  }
}
```

## Best Practices

### 1. Signal Best Practices

```typescript
// ✅ Good: Use computed for derived state
const fullName = computed(() => `${firstName()} ${lastName()}`);

// ❌ Bad: Manual updates for derived state
const fullName = signal('');
effect(() => {
  fullName.set(`${firstName()} ${lastName()}`);
});

// ✅ Good: Use update for state transformations
todos.update(current => [...current, newTodo]);

// ❌ Bad: Read then set pattern
const currentTodos = todos();
todos.set([...currentTodos, newTodo]);

// ✅ Good: Read-only public signals
private _count = signal(0);
count = this._count.asReadonly();

// ❌ Bad: Exposing writable signals directly
count = signal(0); // Can be modified from outside
```

### 2. RxJS Best Practices

```typescript
// ✅ Good: Use takeUntil for component cleanup
export class MyComponent implements OnDestroy {
  private destroy$ = new Subject<void>();
  
  ngOnInit() {
    this.dataService.getData().pipe(
      takeUntil(this.destroy$)
    ).subscribe();
  }
  
  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}

// ✅ Good: Use async pipe in template
@Component({
  template: `<div *ngFor="let item of items$ | async">{{ item.name }}</div>`
})
export class ListComponent {
  items$ = this.dataService.getItems();
}

// ✅ Good: Handle errors appropriately
getData() {
  return this.http.get('/api/data').pipe(
    retry(3),
    catchError(error => {
      console.error('API Error:', error);
      return of([]);
    })
  );
}

// ✅ Good: Use shareReplay for expensive operations
const config$ = this.http.get('/api/config').pipe(
  shareReplay(1)
);
```

### 3. State Management Best Practices

```typescript
// ✅ Good: Immutable updates
addTodo(todo: Todo) {
  this.todos.update(current => [...current, todo]);
}

// ❌ Bad: Mutating state directly
addTodo(todo: Todo) {
  this.todos().push(todo); // Mutates the array
}

// ✅ Good: Single source of truth
@Injectable({ providedIn: 'root' })
export class UserService {
  private _user = signal<User | null>(null);
  user = this._user.asReadonly();
}

// ❌ Bad: Multiple sources of truth
export class ComponentA {
  user = signal<User | null>(null);
}
export class ComponentB {
  user = signal<User | null>(null);
}

// ✅ Good: Meaningful names and structure
interface AppState {
  user: UserState;
  products: ProductState;
  ui: UIState;
}

// ❌ Bad: Flat, unclear structure
interface AppState {
  users: User[];
  selectedUser: User;
  products: Product[];
  isLoading: boolean; // Loading what?
  error: string; // Error for what?
}
```

## Migration Strategies

### From Observables to Signals

```typescript
// Before: Observable-based service
@Injectable({ providedIn: 'root' })
export class OldUserService {
  private userSubject = new BehaviorSubject<User | null>(null);
  user$ = this.userSubject.asObservable();
  
  setUser(user: User) {
    this.userSubject.next(user);
  }
}

// After: Signal-based service
@Injectable({ providedIn: 'root' })
export class NewUserService {
  private _user = signal<User | null>(null);
  user = this._user.asReadonly();
  
  setUser(user: User) {
    this._user.set(user);
  }
}

// Migration helper: Support both during transition
@Injectable({ providedIn: 'root' })
export class HybridUserService {
  private _user = signal<User | null>(null);
  
  // Signal API
  user = this._user.asReadonly();
  
  // Observable API for backward compatibility
  user$ = toObservable(this._user);
  
  setUser(user: User) {
    this._user.set(user);
  }
}
```

### Gradual NgRx to Custom State Migration

```typescript
// Step 1: Create signal-based service alongside NgRx
@Injectable({ providedIn: 'root' })
export class NewUserService {
  private _users = signal<User[]>([]);
  users = this._users.asReadonly();
  
  // Sync with NgRx during migration
  constructor(private store: Store) {
    this.store.select(selectUsers).subscribe(users => {
      this._users.set(users);
    });
  }
}

// Step 2: Components can use either
@Component({})
export class UserComponent {
  // Old way
  users$ = this.store.select(selectUsers);
  
  // New way
  users = this.newUserService.users;
  
  constructor(
    private store: Store,
    private newUserService: NewUserService
  ) {}
}

// Step 3: Remove NgRx dependencies after full migration
```

## Performance Considerations

### Signal Performance Benefits

```typescript
// ✅ Signals provide fine-grained reactivity
@Component({
  template: `
    <div>{{ user.name() }}</div>  <!-- Only updates when name changes -->
    <div>{{ user.age() }}</div>   <!-- Only updates when age changes -->
  `
})
export class UserComponent {
  user = signal({ name: 'John', age: 30 });
  
  updateName() {
    this.user.update(u => ({ ...u, name: 'Jane' }));
    // Only the name div will re-render
  }
}

// ❌ Traditional change detection updates entire component
@Component({
  template: `
    <div>{{ user.name }}</div>
    <div>{{ user.age }}</div>
  `
})
export class UserComponent {
  user = { name: 'John', age: 30 };
  
  updateName() {
    this.user = { ...this.user, name: 'Jane' };
    // Entire component re-renders
  }
}
```

### RxJS Performance Tips

```typescript
// ✅ Use shareReplay to prevent duplicate HTTP calls
const users$ = this.http.get<User[]>('/api/users').pipe(
  shareReplay(1)
);

// ✅ Use debounceTime for user input
searchInput$.pipe(
  debounceTime(300),
  distinctUntilChanged()
);

// ✅ Use OnPush change detection with observables
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<div *ngFor="let item of items$ | async">{{ item.name }}</div>`
})
export class OptimizedComponent {
  items$ = this.dataService.getItems();
}

// ✅ Unsubscribe to prevent memory leaks
export class Component implements OnDestroy {
  private destroy$ = new Subject<void>();
  
  ngOnInit() {
    this.observable$.pipe(
      takeUntil(this.destroy$)
    ).subscribe();
  }
  
  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

### State Management Performance

```typescript
// ✅ Use computed signals for expensive calculations
export class ProductService {
  private _products = signal<Product[]>([]);
  private _filters = signal<ProductFilter>({});
  
  // Computed only recalculates when dependencies change
  filteredProducts = computed(() => {
    const products = this._products();
    const filters = this._filters();
    
    return products.filter(product => {
      // Expensive filtering logic
      return this.matchesFilters(product, filters);
    });
  });
}

// ✅ Batch state updates
updateMultipleFields(updates: Partial<User>) {
  this._user.update(current => ({
    ...current,
    ...updates
  }));
  // Single update instead of multiple set() calls
}

// ✅ Use OnPush with signals
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div>{{ user.name() }}</div>
    <div>{{ expensiveComputation() }}</div>
  `
})
export class OptimizedComponent {
  user = this.userService.user;
  
  // Computed signal - only recalculates when dependencies change
  expensiveComputation = computed(() => {
    return this.performExpensiveCalculation(this.user());
  });
}
```

---

## Additional Resources

- [Angular Signals Guide](https://angular.io/guide/signals)
- [RxJS Official Documentation](https://rxjs.dev/)
- [NgRx Documentation](https://ngrx.io/)
- [Angular Architecture Patterns](https://angular.io/guide/architecture)

## Conclusion

Choose your state management approach based on:

- **Simple local state**: Use Signals
- **Complex async operations**: Use RxJS Observables  
- **Global state in small/medium apps**: Custom service with Signals
- **Global state in large/complex apps**: Consider NgRx or similar libraries
- **Performance-critical apps**: Prefer Signals with OnPush change detection

Remember: You can mix and match these approaches in the same application. Use `toSignal()` and `toObservable()` to