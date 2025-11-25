---
name: angular
description: Expert knowledge in Angular including components, services, dependency injection, routing, forms, RxJS, HTTP client, and testing with Jasmine and Karma.
allowed-tools: [Read, Write, Edit, Bash]
---

# Angular Skill

Comprehensive knowledge for building enterprise-scale applications with Angular.

## Quick Start

### Installation

```bash
# Install Angular CLI globally
npm install -g @angular/cli

# Create new Angular app
ng new my-app

# Interactive prompts will ask:
# - Routing? Yes
# - Stylesheet format? CSS/SCSS/Less/Sass

cd my-app

# Start development server
ng serve

# Open http://localhost:4200
```

### Project Structure

```
my-app/
├── src/
│   ├── app/
│   │   ├── app.component.ts      # Root component
│   │   ├── app.component.html    # Root template
│   │   ├── app.component.css     # Root styles
│   │   ├── app.component.spec.ts # Root tests
│   │   ├── app.module.ts         # Root module
│   │   └── app-routing.module.ts # Routing configuration
│   ├── assets/                   # Static assets
│   ├── environments/             # Environment configs
│   ├── index.html                # Main HTML
│   ├── main.ts                   # Bootstrap entry
│   └── styles.css                # Global styles
├── angular.json                  # Angular configuration
├── tsconfig.json                 # TypeScript configuration
└── package.json
```

### Basic Component

```typescript
// app.component.ts
import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'my-app';
  count = 0;

  increment() {
    this.count++;
  }
}
```

```html
<!-- app.component.html -->
<h1>{{ title }}</h1>
<p>Count: {{ count }}</p>
<button (click)="increment()">Increment</button>
```

---

## Components

### Creating Components

```bash
# Generate component
ng generate component user-profile
# or shorthand
ng g c user-profile

# Generates:
# - user-profile.component.ts
# - user-profile.component.html
# - user-profile.component.css
# - user-profile.component.spec.ts
```

### Component Decorator

```typescript
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-user-profile',
  templateUrl: './user-profile.component.html',
  styleUrls: ['./user-profile.component.css']
})
export class UserProfileComponent implements OnInit {
  user = {
    name: 'John Doe',
    email: 'john@example.com'
  };

  constructor() { }

  ngOnInit(): void {
    // Initialize component
    console.log('Component initialized');
  }
}
```

### Inline Template & Styles

```typescript
@Component({
  selector: 'app-greeting',
  template: `
    <h1>{{ greeting }}</h1>
    <p>Welcome!</p>
  `,
  styles: [`
    h1 { color: blue; }
    p { font-size: 1.2rem; }
  `]
})
export class GreetingComponent {
  greeting = 'Hello, Angular!';
}
```

---

## Data Binding

### Interpolation

```typescript
export class AppComponent {
  name = 'John';
  age = 30;
  getGreeting() {
    return `Hello, ${this.name}!`;
  }
}
```

```html
<h1>{{ name }}</h1>
<p>Age: {{ age }}</p>
<p>{{ getGreeting() }}</p>
<p>{{ age > 18 ? 'Adult' : 'Minor' }}</p>
```

### Property Binding

```typescript
export class AppComponent {
  imageUrl = 'https://example.com/image.jpg';
  isDisabled = false;
}
```

```html
<!-- Bind to element properties -->
<img [src]="imageUrl" alt="Image">
<button [disabled]="isDisabled">Click me</button>

<!-- Alternative syntax -->
<img bind-src="imageUrl">
```

### Event Binding

```typescript
export class AppComponent {
  handleClick() {
    console.log('Button clicked!');
  }

  handleInput(event: Event) {
    const input = event.target as HTMLInputElement;
    console.log(input.value);
  }
}
```

```html
<button (click)="handleClick()">Click me</button>
<input (input)="handleInput($event)" />

<!-- Alternative syntax -->
<button on-click="handleClick()">Click me</button>
```

### Two-Way Binding

```typescript
import { FormsModule } from '@angular/forms';

export class AppComponent {
  name = '';
}
```

```html
<input [(ngModel)]="name" placeholder="Enter name">
<p>Hello, {{ name }}!</p>
```

---

## Directives

### Structural Directives

#### *ngIf

```html
<div *ngIf="isLoggedIn">Welcome back!</div>
<div *ngIf="!isLoggedIn">Please log in</div>

<!-- With else -->
<div *ngIf="isLoggedIn; else loggedOut">
  Welcome back!
</div>
<ng-template #loggedOut>
  <div>Please log in</div>
</ng-template>

<!-- With then and else -->
<div *ngIf="user; then loggedIn else loggedOut"></div>
<ng-template #loggedIn>
  <p>Welcome, {{ user.name }}!</p>
</ng-template>
<ng-template #loggedOut>
  <p>Please log in</p>
</ng-template>
```

#### *ngFor

```typescript
export class AppComponent {
  users = [
    { id: 1, name: 'Alice' },
    { id: 2, name: 'Bob' },
    { id: 3, name: 'Charlie' }
  ];
}
```

```html
<ul>
  <li *ngFor="let user of users">{{ user.name }}</li>
</ul>

<!-- With index -->
<ul>
  <li *ngFor="let user of users; let i = index">
    {{ i + 1 }}. {{ user.name }}
  </li>
</ul>

<!-- With trackBy for performance -->
<ul>
  <li *ngFor="let user of users; trackBy: trackByUserId">
    {{ user.name }}
  </li>
</ul>
```

```typescript
trackByUserId(index: number, user: any): number {
  return user.id;
}
```

#### *ngSwitch

```html
<div [ngSwitch]="status">
  <p *ngSwitchCase="'loading'">Loading...</p>
  <p *ngSwitchCase="'success'">Success!</p>
  <p *ngSwitchCase="'error'">Error occurred</p>
  <p *ngSwitchDefault>Unknown status</p>
</div>
```

### Attribute Directives

#### ngClass

```html
<div [ngClass]="'active'">Single class</div>
<div [ngClass]="['active', 'highlight']">Multiple classes</div>
<div [ngClass]="{ 'active': isActive, 'disabled': isDisabled }">
  Conditional classes
</div>
```

#### ngStyle

```html
<div [ngStyle]="{ 'color': 'blue', 'font-size': '20px' }">
  Styled text
</div>

<div [ngStyle]="{ 'background-color': isActive ? 'green' : 'red' }">
  Conditional style
</div>
```

---

## Component Communication

### Input (Parent to Child)

```typescript
// child.component.ts
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-child',
  template: `<p>{{ message }}</p>`
})
export class ChildComponent {
  @Input() message: string = '';
  @Input() user!: User;
}
```

```html
<!-- parent.component.html -->
<app-child [message]="'Hello from parent'" [user]="currentUser"></app-child>
```

### Output (Child to Parent)

```typescript
// child.component.ts
import { Component, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-child',
  template: `<button (click)="sendMessage()">Send</button>`
})
export class ChildComponent {
  @Output() messageEvent = new EventEmitter<string>();

  sendMessage() {
    this.messageEvent.emit('Hello from child');
  }
}
```

```html
<!-- parent.component.html -->
<app-child (messageEvent)="receiveMessage($event)"></app-child>
```

```typescript
// parent.component.ts
receiveMessage(message: string) {
  console.log(message);
}
```

---

## Services & Dependency Injection

### Creating Services

```bash
ng generate service user
# or
ng g s user
```

```typescript
// user.service.ts
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root' // Available app-wide
})
export class UserService {
  private users = [
    { id: 1, name: 'Alice' },
    { id: 2, name: 'Bob' }
  ];

  getUsers() {
    return this.users;
  }

  getUserById(id: number) {
    return this.users.find(user => user.id === id);
  }

  addUser(name: string) {
    const id = this.users.length + 1;
    this.users.push({ id, name });
  }
}
```

### Using Services

```typescript
// user-list.component.ts
import { Component, OnInit } from '@angular/core';
import { UserService } from '../user.service';

@Component({
  selector: 'app-user-list',
  templateUrl: './user-list.component.html'
})
export class UserListComponent implements OnInit {
  users: any[] = [];

  constructor(private userService: UserService) { }

  ngOnInit() {
    this.users = this.userService.getUsers();
  }
}
```

---

## HTTP Client

### Setup

```typescript
// app.module.ts
import { HttpClientModule } from '@angular/common/http';

@NgModule({
  imports: [
    HttpClientModule
  ]
})
export class AppModule { }
```

### Making HTTP Requests

```typescript
// api.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

interface User {
  id: number;
  name: string;
  email: string;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'https://api.example.com';

  constructor(private http: HttpClient) { }

  // GET request
  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(`${this.apiUrl}/users`);
  }

  // GET by ID
  getUser(id: number): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/users/${id}`);
  }

  // POST request
  createUser(user: User): Observable<User> {
    return this.http.post<User>(`${this.apiUrl}/users`, user);
  }

  // PUT request
  updateUser(id: number, user: User): Observable<User> {
    return this.http.put<User>(`${this.apiUrl}/users/${id}`, user);
  }

  // DELETE request
  deleteUser(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/users/${id}`);
  }

  // With headers
  getUsersWithAuth(): Observable<User[]> {
    const headers = new HttpHeaders({
      'Authorization': 'Bearer token',
      'Content-Type': 'application/json'
    });

    return this.http.get<User[]>(`${this.apiUrl}/users`, { headers });
  }
}
```

### Using HTTP Service

```typescript
export class UserListComponent implements OnInit {
  users: User[] = [];
  loading = false;
  error = '';

  constructor(private apiService: ApiService) { }

  ngOnInit() {
    this.loading = true;

    this.apiService.getUsers().subscribe({
      next: (data) => {
        this.users = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load users';
        this.loading = false;
        console.error(err);
      }
    });
  }
}
```

---

## Routing

### Setup

```typescript
// app-routing.module.ts
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { AboutComponent } from './about/about.component';
import { UserDetailComponent } from './user-detail/user-detail.component';

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'about', component: AboutComponent },
  { path: 'users/:id', component: UserDetailComponent },
  { path: '**', redirectTo: '' } // Wildcard route
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
```

```html
<!-- app.component.html -->
<nav>
  <a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{exact: true}">Home</a>
  <a routerLink="/about" routerLinkActive="active">About</a>
</nav>

<router-outlet></router-outlet>
```

### Programmatic Navigation

```typescript
import { Router } from '@angular/router';

export class UserListComponent {
  constructor(private router: Router) { }

  viewUser(id: number) {
    this.router.navigate(['/users', id]);
  }

  goToAbout() {
    this.router.navigate(['/about'], { queryParams: { page: 1 } });
  }
}
```

### Route Parameters

```typescript
import { ActivatedRoute } from '@angular/router';

export class UserDetailComponent implements OnInit {
  userId: number = 0;

  constructor(private route: ActivatedRoute) { }

  ngOnInit() {
    // Snapshot (one-time read)
    this.userId = Number(this.route.snapshot.paramMap.get('id'));

    // Observable (reactive)
    this.route.paramMap.subscribe(params => {
      this.userId = Number(params.get('id'));
    });

    // Query params
    this.route.queryParams.subscribe(params => {
      console.log(params['page']);
    });
  }
}
```

### Route Guards

```typescript
// auth.guard.ts
import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(private router: Router) { }

  canActivate(): boolean {
    const isAuthenticated = !!localStorage.getItem('token');

    if (!isAuthenticated) {
      this.router.navigate(['/login']);
      return false;
    }

    return true;
  }
}
```

```typescript
// app-routing.module.ts
const routes: Routes = [
  { path: 'dashboard', component: DashboardComponent, canActivate: [AuthGuard] }
];
```

---

## Forms

### Template-Driven Forms

```typescript
import { FormsModule } from '@angular/forms';

@NgModule({
  imports: [FormsModule]
})
export class AppModule { }
```

```typescript
export class LoginComponent {
  user = {
    email: '',
    password: ''
  };

  onSubmit() {
    console.log('Form submitted', this.user);
  }
}
```

```html
<form #loginForm="ngForm" (ngSubmit)="onSubmit()">
  <input
    type="email"
    name="email"
    [(ngModel)]="user.email"
    required
    #email="ngModel"
  />
  <div *ngIf="email.invalid && email.touched">
    Email is required
  </div>

  <input
    type="password"
    name="password"
    [(ngModel)]="user.password"
    required
    minlength="6"
  />

  <button [disabled]="loginForm.invalid">Submit</button>
</form>
```

### Reactive Forms

```typescript
import { ReactiveFormsModule } from '@angular/forms';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html'
})
export class LoginComponent implements OnInit {
  loginForm!: FormGroup;

  constructor(private fb: FormBuilder) { }

  ngOnInit() {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  onSubmit() {
    if (this.loginForm.valid) {
      console.log(this.loginForm.value);
    }
  }

  get email() {
    return this.loginForm.get('email');
  }

  get password() {
    return this.loginForm.get('password');
  }
}
```

```html
<form [formGroup]="loginForm" (ngSubmit)="onSubmit()">
  <input type="email" formControlName="email" />
  <div *ngIf="email?.invalid && email?.touched">
    <div *ngIf="email?.errors?.['required']">Email is required</div>
    <div *ngIf="email?.errors?.['email']">Invalid email</div>
  </div>

  <input type="password" formControlName="password" />
  <div *ngIf="password?.invalid && password?.touched">
    <div *ngIf="password?.errors?.['required']">Password is required</div>
    <div *ngIf="password?.errors?.['minlength']">Min 6 characters</div>
  </div>

  <button [disabled]="loginForm.invalid">Submit</button>
</form>
```

---

## Observables & RxJS

### Basic Observable

```typescript
import { Observable } from 'rxjs';

const observable = new Observable(subscriber => {
  subscriber.next(1);
  subscriber.next(2);
  subscriber.next(3);
  subscriber.complete();
});

observable.subscribe({
  next: (value) => console.log(value),
  complete: () => console.log('Complete')
});
```

### Common Operators

```typescript
import { map, filter, tap, catchError } from 'rxjs/operators';
import { of } from 'rxjs';

this.apiService.getUsers().pipe(
  tap(data => console.log('Raw data:', data)),
  map(users => users.filter(u => u.active)),
  catchError(error => {
    console.error('Error:', error);
    return of([]);
  })
).subscribe(users => {
  this.users = users;
});
```

### Subject

```typescript
import { Subject } from 'rxjs';

export class DataService {
  private dataSubject = new Subject<string>();
  data$ = this.dataSubject.asObservable();

  emitData(value: string) {
    this.dataSubject.next(value);
  }
}
```

---

## Lifecycle Hooks

```typescript
export class UserComponent implements OnInit, OnDestroy, OnChanges {
  @Input() userId!: number;

  ngOnChanges(changes: SimpleChanges) {
    console.log('Input changed:', changes);
  }

  ngOnInit() {
    console.log('Component initialized');
  }

  ngOnDestroy() {
    console.log('Component destroyed');
  }
}
```

All lifecycle hooks:
- `ngOnChanges` - Input properties changed
- `ngOnInit` - Component initialized
- `ngDoCheck` - Change detection run
- `ngAfterContentInit` - Content projection initialized
- `ngAfterContentChecked` - Content projection checked
- `ngAfterViewInit` - View initialized
- `ngAfterViewChecked` - View checked
- `ngOnDestroy` - Component destroyed

---

## Testing

### Component Testing

```typescript
// user.component.spec.ts
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { UserComponent } from './user.component';

describe('UserComponent', () => {
  let component: UserComponent;
  let fixture: ComponentFixture<UserComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UserComponent ]
    }).compileComponents();

    fixture = TestBed.createComponent(UserComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display user name', () => {
    component.user = { name: 'John', email: 'john@example.com' };
    fixture.detectChanges();

    const compiled = fixture.nativeElement;
    expect(compiled.querySelector('h1').textContent).toContain('John');
  });
});
```

### Service Testing

```typescript
import { TestBed } from '@angular/core/testing';
import { UserService } from './user.service';

describe('UserService', () => {
  let service: UserService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(UserService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should return users', () => {
    const users = service.getUsers();
    expect(users.length).toBeGreaterThan(0);
  });
});
```

---

## Best Practices

### 1. Use OnPush Change Detection

```typescript
@Component({
  selector: 'app-user',
  templateUrl: './user.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class UserComponent { }
```

### 2. Unsubscribe from Observables

```typescript
import { Subscription } from 'rxjs';

export class UserComponent implements OnInit, OnDestroy {
  private subscription = new Subscription();

  ngOnInit() {
    this.subscription.add(
      this.apiService.getUsers().subscribe(users => {
        this.users = users;
      })
    );
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }
}
```

### 3. Use Async Pipe

```typescript
export class UserComponent {
  users$ = this.apiService.getUsers();

  constructor(private apiService: ApiService) { }
}
```

```html
<div *ngFor="let user of users$ | async">
  {{ user.name }}
</div>
```

### 4. Lazy Loading Modules

```typescript
const routes: Routes = [
  {
    path: 'admin',
    loadChildren: () => import('./admin/admin.module').then(m => m.AdminModule)
  }
];
```

---

## Resources

- **Official Docs:** https://angular.io/docs
- **CLI Docs:** https://angular.io/cli
- **Style Guide:** https://angular.io/guide/styleguide
- **RxJS:** https://rxjs.dev
- **GitHub:** https://github.com/angular/angular

---

## Troubleshooting

### Module Not Found

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Build Errors

```bash
# Clear cache
ng cache clean

# Rebuild
ng build
```

This comprehensive skill covers Angular with components, services, routing, forms, HTTP, and best practices!
